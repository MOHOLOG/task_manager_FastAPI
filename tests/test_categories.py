async def test_create_category(client, user_headers):
    response = await client.post(
        "/categories", json={"name": "Work"}, headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["category name"] == "Work"


async def test_create_category_requires_auth(client):
    response = await client.post("/categories", json={"name": "Work"})
    assert response.status_code == 401


async def test_get_categories(client, user_headers):
    await client.post("/categories", json={"name": "Work"}, headers=user_headers)
    await client.post("/categories", json={"name": "Home"}, headers=user_headers)

    response = await client.get("/categories", headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    names = [category["name"] for category in data["categories"]]
    assert "Work" in names
    assert "Home" in names


async def test_edit_category(client, user_headers):
    await client.post("/categories", json={"name": "Old"}, headers=user_headers)
    listing = await client.get("/categories", headers=user_headers)
    category_id = listing.json()["categories"][0]["id"]

    response = await client.patch(
        f"/categories/{category_id}",
        params={"new_name": "New"},
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["new category name"] == "New"


async def test_edit_category_to_existing_name(client, user_headers):
    await client.post("/categories", json={"name": "First"}, headers=user_headers)
    await client.post("/categories", json={"name": "Second"}, headers=user_headers)
    listing = await client.get("/categories", headers=user_headers)
    second = next(
        category for category in listing.json()["categories"] if category["name"] == "Second"
    )

    response = await client.patch(
        f"/categories/{second['id']}",
        params={"new_name": "First"},
        headers=user_headers,
    )

    assert response.status_code == 400


async def test_delete_category(client, user_headers):
    await client.post("/categories", json={"name": "Trash"}, headers=user_headers)
    listing = await client.get("/categories", headers=user_headers)
    category_id = listing.json()["categories"][0]["id"]

    response = await client.delete(f"/categories/{category_id}", headers=user_headers)
    assert response.status_code == 200

    after = await client.get("/categories", headers=user_headers)
    assert after.json()["total"] == 0


async def test_delete_missing_category(client, user_headers):
    response = await client.delete("/categories/9999", headers=user_headers)
    assert response.status_code == 404
