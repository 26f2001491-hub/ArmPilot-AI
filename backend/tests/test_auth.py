from httpx import AsyncClient

REGISTER_PAYLOAD = {"email": "auth-test@example.com", "password": "supersecret123"}


async def test_register_success(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201

    body = response.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert body["is_active"] is True
    assert "hashed_password" not in body


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_login_success_and_read_current_user(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    login_response = await client.post("/api/v1/auth/login", json=REGISTER_PAYLOAD)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_read_current_user_without_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
