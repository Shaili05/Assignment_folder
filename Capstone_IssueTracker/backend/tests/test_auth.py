import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def test_get_me_without_token(client):
    """No token provided - should return 401"""
    response = client.get("/api/users/me")
    assert response.status_code == 401

def test_get_me_with_valid_token(client):
    """Valid token - should return user info"""
    client.post("/api/users/register", json={
        "name": "Auth Test User",
        "email": "authtest@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    login_response = client.post("/api/users/login", json={
        "email": "authtest@example.com",
        "password": b64("Test@123")
    })
    token = login_response.json()["access_token"]
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "authtest@example.com"

def test_admin_endpoint_blocked_for_member(client):
    """Member trying to access admin endpoint - should return 403"""
    client.post("/api/users/register", json={
        "name": "Member User",
        "email": "member@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    login_response = client.post("/api/users/login", json={
        "email": "member@example.com",
        "password": b64("Test@123")
    })
    token = login_response.json()["access_token"]
    response = client.get(
        "/api/users/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_admin_endpoint_accessible_for_admin(client):
    """Admin accessing admin endpoint - should return 200"""
    client.post("/api/users/register", json={
        "name": "Admin User",
        "email": "admin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    login_response = client.post("/api/users/login", json={
        "email": "admin@example.com",
        "password": b64("Test@123")
    })
    token = login_response.json()["access_token"]
    response = client.get(
        "/api/users/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_get_me_with_invalid_token(client):
    """Fake token - should return 401"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer faketoken123"}
    )
    assert response.status_code == 401