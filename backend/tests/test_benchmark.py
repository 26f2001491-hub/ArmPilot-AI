from httpx import AsyncClient


async def test_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/benchmark")
    assert response.status_code == 401


async def test_create_and_list_benchmark(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "model_name": "llama-3-8b",
        "runtime": "onnxruntime",
        "quantization": "Q4_0",
        "latency_ms": 500,
        "generated_tokens": 100,
    }
    created = await client.post("/api/v1/benchmark", json=payload, headers=auth_headers)
    assert created.status_code == 201
    body = created.json()
    assert body["model_name"] == "llama-3-8b"
    # throughput derived from latency + tokens: 100 tokens / 0.5s = 200 tps
    assert body["throughput_tps"] == 200.0

    listing = await client.get("/api/v1/benchmark", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


async def test_get_and_delete_benchmark(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await client.post(
        "/api/v1/benchmark",
        json={"model_name": "phi-3", "generated_tokens": 10},
        headers=auth_headers,
    )
    bid = created.json()["id"]

    fetched = await client.get(f"/api/v1/benchmark/{bid}", headers=auth_headers)
    assert fetched.status_code == 200

    deleted = await client.delete(f"/api/v1/benchmark/{bid}", headers=auth_headers)
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/benchmark/{bid}", headers=auth_headers)
    assert missing.status_code == 404
