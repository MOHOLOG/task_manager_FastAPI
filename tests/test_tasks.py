async def test_create_task(client, user_headers):
    response = await client.post(
        "/tasks", json={"title": "Buy milk"}, headers=user_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_title"] == "Buy milk"
    assert data["category"] is None
    assert data["amount of subtasks"] == 0


async def test_create_task_with_category_and_subtasks(client, user_headers):
    await client.post("/categories", json={"name": "Work"}, headers=user_headers)

    payload = {
        "title": "Big task",
        "category_name": "Work",
        "subtasks": [{"title": "Step 1"}, {"title": "Step 2"}],
    }
    response = await client.post("/tasks", json=payload, headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Work"
    assert data["amount of subtasks"] == 2


async def test_create_task_with_unknown_category(client, user_headers):
    response = await client.post(
        "/tasks",
        json={"title": "Orphan", "category_name": "Does not exist"},
        headers=user_headers,
    )
    assert response.status_code == 404


async def test_tasks_require_auth(client):
    response = await client.get("/tasks")
    assert response.status_code == 401


async def test_get_tasks(client, user_headers):
    await client.post("/tasks", json={"title": "Task A"}, headers=user_headers)
    await client.post("/tasks", json={"title": "Task B"}, headers=user_headers)

    response = await client.get("/tasks", headers=user_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["tasks"]) == 2


async def test_get_tasks_with_search(client, user_headers):
    await client.post("/tasks", json={"title": "Buy milk"}, headers=user_headers)
    await client.post("/tasks", json={"title": "Read book"}, headers=user_headers)

    response = await client.get(
        "/tasks", params={"title": "milk"}, headers=user_headers
    )

    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "Buy milk"


async def test_get_tasks_pagination(client, user_headers):
    for index in range(3):
        await client.post(
            "/tasks", json={"title": f"Task {index}"}, headers=user_headers
        )

    response = await client.get(
        "/tasks", params={"skip": 0, "limit": 2}, headers=user_headers
    )

    data = response.json()
    assert len(data["tasks"]) == 2
    assert data["total"] == 3
    assert data["has_more"] is True


async def test_get_single_task(client, user_headers):
    created = await client.post(
        "/tasks", json={"title": "Solo"}, headers=user_headers
    )
    task_id = created.json()["task_id"]

    response = await client.get(f"/tasks/{task_id}", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Solo"


async def test_get_missing_task(client, user_headers):
    response = await client.get("/tasks/9999", headers=user_headers)
    assert response.status_code == 404


async def test_edit_task(client, user_headers):
    created = await client.post(
        "/tasks", json={"title": "Old title"}, headers=user_headers
    )
    task_id = created.json()["task_id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "New title", "done": True},
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["new_title"] == "New title"

    check = await client.get(f"/tasks/{task_id}", headers=user_headers)
    assert check.json()["title"] == "New title"
    assert check.json()["done"] is True


async def test_delete_task(client, user_headers):
    created = await client.post(
        "/tasks", json={"title": "To delete"}, headers=user_headers
    )
    task_id = created.json()["task_id"]

    response = await client.delete(f"/tasks/{task_id}", headers=user_headers)
    assert response.status_code == 200

    check = await client.get(f"/tasks/{task_id}", headers=user_headers)
    assert check.status_code == 404


async def test_add_and_get_subtasks(client, user_headers):
    created = await client.post(
        "/tasks", json={"title": "Parent"}, headers=user_headers
    )
    task_id = created.json()["task_id"]

    response = await client.post(
        f"/tasks/{task_id}/subtasks",
        json={"title": "Child"},
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["subtask title"] == "Child"

    listing = await client.get(f"/tasks/{task_id}/subtasks", headers=user_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["tasks"][0]["title"] == "Child"


async def test_add_subtask_to_missing_parent(client, user_headers):
    response = await client.post(
        "/tasks/9999/subtasks", json={"title": "Child"}, headers=user_headers
    )
    assert response.status_code == 404


async def test_user_cannot_access_another_users_task(client, user_headers):
    created = await client.post(
        "/tasks", json={"title": "Private"}, headers=user_headers
    )
    task_id = created.json()["task_id"]

    await client.post(
        "/register", json={"username": "other", "password": "password123"}
    )
    login = await client.post(
        "/login", json={"username": "other", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await client.get(f"/tasks/{task_id}", headers=other_headers)
    assert response.status_code == 404
