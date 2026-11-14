async def test_users_list_forbidden_for_regular_user(client, user_headers):
    response = await client.get("/users", headers=user_headers)
    assert response.status_code == 403


async def test_users_list_allowed_for_admin(client, admin_headers):
    response = await client.get("/users", headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    usernames = [user["username"] for user in data["users"]]
    assert "admin" in usernames


async def test_edit_user_password_and_username(client, user_headers):
    response = await client.patch(
        "/users/me",
        json={
            "username": "tester2",
            "current_password": "testerpass",
            "password": "newpassword123",
        },
        headers=user_headers,
    )

    assert response.status_code == 200

    login = await client.post(
        "/login", json={"username": "tester2", "password": "newpassword123"}
    )
    assert login.status_code == 200


async def test_edit_user_with_wrong_current_password(client, user_headers):
    response = await client.patch(
        "/users/me",
        json={"current_password": "wrongpass123", "password": "newpassword123"},
        headers=user_headers,
    )

    assert response.status_code == 400
