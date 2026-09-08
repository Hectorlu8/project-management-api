

def test_register_user_returns_201_without_password_fields(client):
    response = client.post(
        "/users/",
        json={"username": "alice", "email": "alice@example.com", "password": "pw123456"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "hashed_password" not in body

def test_get_users_returns_200_with_valid_token(client, auth_headers):
    response = client.get("/users/", headers=auth_headers)
    assert response.status_code == 200


    
def test_login_user_returns_401_with_invalid_credentials(client):
    client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )

    response = client.post(
        "/token/",
        data={"username": "hector@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    
def test_get_users_returns_401_with_invalid_credentials(client):
    response = client.get("/users/")
    assert response.status_code == 401    
    
def test_get_users_returns_200_with_valid_token(client):
    client.post(
        "/users/",
        json={"username": "hector", "email": "hector@example.com", "password": "pw123456"},
    )

    login_response = client.post(
        "/token/",
        data={"username": "hector@example.com", "password": "pw123456"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200