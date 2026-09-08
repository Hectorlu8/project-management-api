def test_get_tasks_returns_404_with_nonexistent_task(client, auth_headers):
    response = client.get("/tasks/999999", headers=auth_headers)
    assert response.status_code == 404
    
def test_post_task_returns_404_with_nonexistent_project(client, auth_headers):
    response = client.post(
        "/tasks/",
        json={"title": "Tarea de hector", "project_id": 999999},
        headers=auth_headers,
    )
    assert response.status_code == 404
    
def test_patch_task_returns_200_with_valid_data(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]

    project_response = client.post(
        "/projects/",
        json={"name": "Proyecto de hector", "owner_id": user_id},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    task_response = client.post(
        "/tasks/",
        json={"title": "Tarea de hector", "project_id": project_id},
        headers=auth_headers,
    )
    task_id = task_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"title": "Tarea de hector actualizada"}, headers=auth_headers)
    assert response.status_code == 200

def test_delete_task_returns_204(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]

    project_response = client.post(
        "/projects/",
        json={"name": "Proyecto de hector", "owner_id": user_id},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    task_response = client.post(
        "/tasks/",
        json={"title": "Tarea de hector", "project_id": project_id},
        headers=auth_headers,
    )
    task_id = task_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    
def test_get_tasks_with_different_priorities(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]

    project_response = client.post(
        "/projects/",
        json={"name": "Proyecto de hector", "owner_id": user_id},
        headers=auth_headers,
    )
    project_id = project_response.json()["id"]

    response1 = client.post(
        "/tasks/",
        json={"title": "Tarea de hector - Alta Prioridad", "project_id": project_id, "priority": "High"},
        headers=auth_headers,
    )
    response2 = client.post(
        "/tasks/",
        json={"title": "Tarea de hector - Baja Prioridad", "project_id": project_id, "priority": "Low"},
        headers=auth_headers,
    )
    response3 = client.post(
        "/tasks/",
        json={"title": "Tarea de hector - Prioridad Media", "project_id": project_id, "priority": "Medium"},
        headers=auth_headers,
    )
    
    response_get = client.get("/tasks/", params={"priority": "High"}, headers=auth_headers)
    tasks = response_get.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "High"
