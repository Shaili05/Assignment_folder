import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def test_register_user_success(client):
    """Test successful user registration"""
    response = client.post("/api/users/register", json={
        "name": "Test User",
        "email": "testuser@test.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@test.com"
    assert data["name"] == "Test User"
    assert data["role"] == "member"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_email(client):
    """Test that duplicate email returns 409"""
    client.post("/api/users/register", json={
        "name": "Test User",
        "email": "duplicate@test.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    response = client.post("/api/users/register", json={
        "name": "Test User 2",
        "email": "duplicate@test.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    assert response.status_code == 409

def test_register_invalid_email(client):
    """Test that invalid email format returns 422"""
    response = client.post("/api/users/register", json={
        "name": "Test User",
        "email": "notanemail",
        "password": b64("Test@123"),
        "role": "member"
    })
    assert response.status_code == 422

def test_register_missing_fields(client):
    """Test that missing required fields returns 422"""
    response = client.post("/api/users/register", json={
        "name": "Test User"
    })
    assert response.status_code == 422

def test_login_success(client):
    """Test successful login returns token"""
    client.post("/api/users/register", json={
        "name": "Test User",
        "email": "testuser@test.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    response = client.post("/api/users/login", json={
        "email": "testuser@test.com",
        "password": b64("Test@123")
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Test wrong password returns 401"""
    client.post("/api/users/register", json={
        "name": "Test User",
        "email": "testuser@test.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    response = client.post("/api/users/login", json={
        "email": "testuser@test.com",
        "password": b64("WrongPassword")
    })
    assert response.status_code == 401

def test_login_nonexistent_email(client):
    """Test login with email that doesn't exist returns 401"""
    response = client.post("/api/users/login", json={
        "email": "nobody@test.com",
        "password": b64("Test@123")
    })
    assert response.status_code == 401