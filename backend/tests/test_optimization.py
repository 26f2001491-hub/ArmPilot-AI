from httpx import AsyncClient


async def test_create_update_delete_profile(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    created = await client.post(
        "/api/v1/optimization",
        json={"name": "8-thread Q4", "thread_count": 8, "quantization": "Q4_0"},
        headers=auth_headers,
    )
    assert created.status_code == 201
    profile = created.json()
    assert profile["thread_count"] == 8
    assert profile["is_active"] is False

    pid = profile["id"]
    updated = await client.patch(
        f"/api/v1/optimization/{pid}",
        json={"is_active": True, "batch_size": 4},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is True
    assert updated.json()["batch_size"] == 4

    deleted = await client.delete(f"/api/v1/optimization/{pid}", headers=auth_headers)
    assert deleted.status_code == 204


async def test_only_one_active_profile(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    first = await client.post(
        "/api/v1/optimization",
        json={"name": "a"},
        headers=auth_headers,
    )
    second = await client.post(
        "/api/v1/optimization",
        json={"name": "b"},
        headers=auth_headers,
    )
    fid = first.json()["id"]
    sid = second.json()["id"]

    await client.patch(f"/api/v1/optimization/{fid}", json={"is_active": True}, headers=auth_headers)
    await client.patch(f"/api/v1/optimization/{sid}", json={"is_active": True}, headers=auth_headers)

    first_after = await client.get(f"/api/v1/optimization/{fid}", headers=auth_headers)
    assert first_after.json()["is_active"] is False
