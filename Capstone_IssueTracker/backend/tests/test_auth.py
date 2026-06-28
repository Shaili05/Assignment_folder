import pytest

# Test 1: Access /me without token - should be blocked
def test_get_me_without_token(client):
    """No token provided - should return 403"""
    response = client.get("/api/users/me")
    assert response.status_code == 401

# Test 2: Access /me with valid token - should work
def test_get_me_with_valid_token(client):
    """Valid token - should return user info"""
    # First register a user
    client.post("/api/users/register", json={
        "name": "Auth Test User",
        "email": "authtest@example.com",
        "password": "Test@123",
        "role": "member"
    })
    # Then login to get token
    login_response = client.post("/api/users/login", json={
        "email": "authtest@example.com",
        "password": "Test@123"
    })
    token = login_response.json()["access_token"]

    # Use token to access /me
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "authtest@example.com"

# Test 3: Access admin endpoint as member - should be blocked
def test_admin_endpoint_blocked_for_member(client):
    """Member trying to access admin endpoint - should return 403"""
    # Register as member
    client.post("/api/users/register", json={
        "name": "Member User",
        "email": "member@example.com",
        "password": "Test@123",
        "role": "member"
    })
    # Login
    login_response = client.post("/api/users/login", json={
        "email": "member@example.com",
        "password": "Test@123"
    })
    token = login_response.json()["access_token"]

    # Try to access admin endpoint
    response = client.get(
        "/api/users/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

# Test 4: Access admin endpoint as admin - should work
def test_admin_endpoint_accessible_for_admin(client):
    """Admin accessing admin endpoint - should return 200"""
    # Register as admin
    client.post("/api/users/register", json={
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Test@123",
        "role": "admin"
    })
    # Login
    login_response = client.post("/api/users/login", json={
        "email": "admin@example.com",
        "password": "Test@123"
    })
    token = login_response.json()["access_token"]

    # Access admin endpoint
    response = client.get(
        "/api/users/admin-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

# Test 5: Invalid token - should be blocked
def test_get_me_with_invalid_token(client):
    """Fake token - should return 403"""
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer faketoken123"}
    )
    assert response.status_code == 401