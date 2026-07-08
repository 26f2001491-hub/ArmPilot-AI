from httpx import AsyncClient


async def test_create_inference_job_runs_echo_runtime(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "model_name": "tinyllama",
        "prompt": "hello world from arm",
        "runtime": "echo",
        "max_tokens": 8,
    }
    created = await client.post("/api/v1/inference", json=payload, headers=auth_headers)
    assert created.status_code == 201
    job = created.json()
    assert job["status"] == "completed"
    assert job["prompt_tokens"] == 4
    assert job["output"] is not None
    assert job["latency_ms"] is not None


async def test_list_and_get_and_delete_job(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await client.post(
        "/api/v1/inference",
        json={"model_name": "m", "prompt": "a b c"},
        headers=auth_headers,
    )
    jid = created.json()["id"]

    listing = await client.get("/api/v1/inference", headers=auth_headers)
    assert listing.status_code == 200
    assert any(j["id"] == jid for j in listing.json())

    fetched = await client.get(f"/api/v1/inference/{jid}", headers=auth_headers)
    assert fetched.status_code == 200

    deleted = await client.delete(f"/api/v1/inference/{jid}", headers=auth_headers)
    assert deleted.status_code == 204
