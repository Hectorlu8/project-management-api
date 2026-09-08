def test_get_projects_returns_404_with_nonexistent_project(client, auth_headers):
    response = client.get("/projects/999999", headers=auth_headers)
    assert response.status_code == 404

def test_post_project_returns_404_with_nonexistent_owner(client, auth_headers):
    response = client.post(
        "/projects/",
        json={"name": "Proyecto de hector", "owner_id": 999999},
        headers=auth_headers,
    )
    assert response.status_code == 404

def test_patch_project_returns_200_with_valid_data(client, auth_headers):
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

    response = client.patch(f"/projects/{project_id}", json={"name": "Proyecto de hector actualizado"}, headers=auth_headers)
    assert response.status_code == 200
    
def test_delete_project_returns_204(client, auth_headers):
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

    response = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

def test_delete_project_returns_409_with_existing_tasks(client, auth_headers):
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

    client.post(
        "/tasks/",
        json={"title": "Tarea de hector", "project_id": project_id},
        headers=auth_headers,
    )

    response = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 409
