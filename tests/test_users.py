def test_get_user_returns_404_with_nonexistent_user(client, auth_headers):
    response = client.get("/users/999999", headers=auth_headers)
    assert response.status_code == 404

def test_patch_user_returns_200_with_valid_data(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]
    response = client.patch(f"/users/{user_id}", json={"username": "hector_updated"}, headers=auth_headers)
    assert response.status_code == 200

    
def test_delete_user_returns_204_without_projects(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]
    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert response.status_code == 204
    
def test_delete_user_returns_400_with_projects(client, auth_headers):
    user_response = client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )
    user_id = user_response.json()["id"]

    client.post(
        "/projects/",
        json={"name": "Proyecto de hector", "owner_id": user_id},
        headers=auth_headers,
    )

    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert response.status_code == 400

    