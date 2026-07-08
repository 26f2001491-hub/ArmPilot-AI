from httpx import AsyncClient


async def test_recommendations_flag_slow_unquantized_run(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    # A slow, unquantized run should score poorly and produce recommendations.
    created = await client.post(
        "/api/v1/benchmark",
        json={
            "model_name": "big-model",
            "quantization": None,
            "ttft_ms": 2500,
            "throughput_tps": 3,
            "generated_tokens": 50,
        },
        headers=auth_headers,
    )
    bid = created.json()["id"]

    report = await client.get(f"/api/v1/recommendation/{bid}", headers=auth_headers)
    assert report.status_code == 200
    body = report.json()
    assert body["benchmark_id"] == bid
    assert body["score"] < 60
    categories = {r["category"] for r in body["recommendations"]}
    assert "latency" in categories
    assert "throughput" in categories
    assert "quantization" in categories


async def test_recommendation_missing_benchmark(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/recommendation/999999", headers=auth_headers)
    assert response.status_code == 404
