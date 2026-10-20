import pytest


def test_list_tasks_requires_authentication(client):
    response = client.get("/tasks")

    assert response.status_code == 401
    assert response.get_json()["code"] == 401


def test_list_tasks_rejects_invalid_token(client):
    response = client.get("/tasks", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
    assert response.get_json()["code"] == 401


def test_list_tasks_returns_an_empty_list(client, auth_headers):
    response = client.get("/tasks", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"code": 200, "message": "Success!", "data": []}


def test_list_tasks_returns_only_the_authenticated_users_tasks(
    client, user, other_user, auth_headers, task_factory
):
    own_task = task_factory(user["id"], title="Own task")
    task_factory(other_user["id"], title="Other user task")

    response = client.get("/tasks", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json()["data"] == [own_task]


def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks", json={"title": "Write integration tests"}, headers=auth_headers
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["code"] == 201
    assert body["data"]["title"] == "Write integration tests"
    assert body["data"]["completed"] is False
    assert body["data"]["id"] is not None


@pytest.mark.parametrize("payload", [{}, {"title": ""}, {"completed": True}])
def test_create_task_requires_a_title(client, auth_headers, payload):
    response = client.post("/tasks", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.get_json() == {
        "code": 400,
        "message": "There are missing fields!",
        "data": None,
    }


def test_get_task(client, user, auth_headers, task_factory):
    task = task_factory(user["id"], title="Read me")

    response = client.get(f"/tasks/{task['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json()["data"] == task


def test_get_task_of_another_user_returns_404(
    client, other_user, auth_headers, task_factory
):
    task = task_factory(other_user["id"], title="Private task")

    response = client.get(f"/tasks/{task['id']}", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json()["data"] is None


def test_get_nonexistent_task_returns_404(client, auth_headers):
    response = client.get("/tasks/999999", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json()["data"] is None


def test_update_task(client, user, auth_headers, task_factory):
    task = task_factory(user["id"], title="Old title")

    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "New title", "completed": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["data"] == {
        "id": task["id"],
        "title": "New title",
        "completed": True,
    }


def test_update_task_accepts_false_completed(client, user, auth_headers, task_factory):
    task = task_factory(user["id"], title="Old title", completed=True)

    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "Still pending", "completed": False},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["completed"] is False


@pytest.mark.parametrize(
    "payload",
    [{}, {"completed": True}, {"title": "Missing completed"}],
)
def test_update_task_requires_title_and_completed(
    client, user, auth_headers, task_factory, payload
):
    task = task_factory(user["id"])

    response = client.put(f"/tasks/{task['id']}", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.get_json() == {
        "code": 400,
        "message": "There are missing fields!",
        "data": None,
    }


def test_update_task_of_another_user_returns_404(
    client, other_user, auth_headers, task_factory
):
    task = task_factory(other_user["id"])

    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "Hijacked", "completed": True},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.get_json()["data"] is None


def test_update_nonexistent_task_returns_404(client, auth_headers):
    response = client.put(
        "/tasks/999999",
        json={"title": "Missing", "completed": False},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.get_json()["data"] is None


def test_delete_task(client, user, auth_headers, task_factory):
    task = task_factory(user["id"])

    response = client.delete(f"/tasks/{task['id']}", headers=auth_headers)

    assert response.status_code == 204
    assert response.data == b""
    assert client.get(f"/tasks/{task['id']}", headers=auth_headers).status_code == 404


def test_delete_task_of_another_user_returns_404(
    client, other_user, auth_headers, other_auth_headers, task_factory
):
    task = task_factory(other_user["id"])

    response = client.delete(f"/tasks/{task['id']}", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json()["data"] is None
    assert (
        client.get(f"/tasks/{task['id']}", headers=other_auth_headers).status_code
        == 200
    )


def test_delete_nonexistent_task_returns_404(client, auth_headers):
    response = client.delete("/tasks/999999", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json()["data"] is None
