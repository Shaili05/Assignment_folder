import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def get_admin_token(client):
    client.post("/api/users/register", json={
        "name": "Admin User",
        "email": "issueadmin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    response = client.post("/api/users/login", json={
        "email": "issueadmin@example.com",
        "password": b64("Test@123")
    })
    return response.json()["access_token"]

def create_test_project(client, token):
    response = client.post("/api/projects/", json={
        "name": "Issue Test Project",
        "description": "For issue tests",
        "project_key": "ITP",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]

def test_create_issue_success(client):
    """Issue creation with valid data should succeed"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    response = client.post("/api/issues/", json={
        "title": "Fix login bug",
        "description": "Login fails on wrong password",
        "issue_type": "bug",
        "priority": "high",
        "project_id": project_id
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fix login bug"
    assert data["status"] == "BACKLOG"

def test_create_issue_invalid_project_id(client):
    """Issue creation with invalid project_id should return 400 or 404"""
    token = get_admin_token(client)
    response = client.post("/api/issues/", json={
        "title": "Test Issue",
        "description": "Test",
        "issue_type": "task",
        "priority": "low",
        "project_id": "invalidid123"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 404]

def test_create_issue_missing_fields(client):
    """Issue creation with missing required fields should return 422"""
    token = get_admin_token(client)
    response = client.post("/api/issues/", json={
        "description": "Missing title and project_id"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422