async def test_register_user(client):
    response = await client.post(
        "/register", json={"username": "alice", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert "created successfully" in data["message"]


async def test_register_duplicate_username(client):
    user = {"username": "bob", "password": "password123"}
    await client.post("/register", json=user)

    response = await client.post("/register", json=user)

    assert response.status_code == 409


async def test_register_with_short_password(client):
    response = await client.post(
        "/register", json={"username": "carol", "password": "123"}
    )
    assert response.status_code == 422


async def test_login_success(client):
    await client.post("/register", json={"username": "dave", "password": "password123"})

    response = await client.post(
        "/login", json={"username": "dave", "password": "password123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


async def test_login_with_wrong_password(client):
    await client.post("/register", json={"username": "erin", "password": "password123"})

    response = await client.post(
        "/login", json={"username": "erin", "password": "wrongpassword"}
    )

    assert response.status_code == 401


async def test_login_with_unknown_user(client):
    response = await client.post(
        "/login", json={"username": "ghost", "password": "password123"}
    )
    assert response.status_code == 401


async def test_me_requires_token(client):
    response = await client.get("/me")
    assert response.status_code == 401


async def test_me_with_valid_token(client):
    await client.post("/register", json={"username": "frank", "password": "password123"})
    login = await client.post(
        "/login", json={"username": "frank", "password": "password123"}
    )
    token = login.json()["access_token"]

    response = await client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == "frank"


async def test_me_with_invalid_token(client):
    response = await client.get(
        "/me", headers={"Authorization": "Bearer this.is.not.a.valid.token"}
    )
    assert response.status_code == 401
