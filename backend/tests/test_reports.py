from httpx import AsyncClient


async def test_report_aggregates_benchmarks(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/v1/benchmark",
        json={"model_name": "m1", "latency_ms": 400, "generated_tokens": 80},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/benchmark",
        json={"model_name": "m2", "latency_ms": 200, "generated_tokens": 80},
        headers=auth_headers,
    )

    created = await client.post(
        "/api/v1/reports",
        json={"title": "Weekly summary"},
        headers=auth_headers,
    )
    assert created.status_code == 201
    report = created.json()
    assert report["data"]["run_count"] == 2
    assert report["data"]["best_model"]["model_name"] == "m2"

    listing = await client.get("/api/v1/reports", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


async def test_history_records_actions(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    await client.post(
        "/api/v1/benchmark",
        json={"model_name": "m", "generated_tokens": 1},
        headers=auth_headers,
    )
    history = await client.get("/api/v1/history", headers=auth_headers)
    assert history.status_code == 200
    actions = [h["action"] for h in history.json()]
    assert "benchmark.create" in actions
