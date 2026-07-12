import base64

def b64(s):
    return base64.b64encode(s.encode()).decode()


def get_admin_token(client):
    client.post("/api/users/register", json={
        "name": "Edge Admin",
        "email": "edgeadmin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    login = client.post("/api/users/login", json={
        "email": "edgeadmin@example.com",
        "password": b64("Test@123")
    })
    return login.json()["access_token"]


def test_get_issue_with_invalid_id_format(client):
    """Malformed ObjectId should return 400, not crash"""
    token = get_admin_token(client)
    response = client.get("/api/issues/not-a-valid-object-id",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_get_nonexistent_project(client):
    """Well-formed but non-existent ObjectId should return 404"""
    token = get_admin_token(client)
    fake_id = "6a4c000000000000000000fa"
    response = client.get(f"/api/projects/{fake_id}",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_create_project_with_empty_name(client):
    """Empty required field should be rejected with 422"""
    token = get_admin_token(client)
    response = client.post("/api/projects/", json={
        "name": "",
        "description": "test",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_create_issue_without_auth_token(client):
    """No token at all should return 401"""
    response = client.post("/api/issues/", json={
        "title": "Test",
        "project_id": "6a4c000000000000000000fa"
    })
    assert response.status_code == 401


def test_member_cannot_delete_project(client):
    """Non-admin role should be blocked from admin-only actions with 403"""
    client.post("/api/users/register", json={
        "name": "Regular Member",
        "email": "regmember@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    login = client.post("/api/users/login", json={
        "email": "regmember@example.com",
        "password": b64("Test@123")
    })
    member_token = login.json()["access_token"]

    admin_token = get_admin_token(client)
    project = client.post("/api/projects/", json={
        "name": "Delete Test Project",
        "description": "test",
        "members": []
    }, headers={"Authorization": f"Bearer {admin_token}"})
    project_id = project.json()["id"]

    response = client.delete(f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {member_token}"})
    assert response.status_code == 403


def test_duplicate_project_name_rejected(client):
    """Creating a project with a name that already exists should fail"""
    token = get_admin_token(client)
    client.post("/api/projects/", json={
        "name": "Unique Project Name",
        "description": "first",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})

    response = client.post("/api/projects/", json={
        "name": "Unique Project Name",
        "description": "duplicate attempt",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409


def test_login_with_wrong_password_format(client):
    """Non-base64 garbage password should return 400, not 500"""
    client.post("/api/users/register", json={
        "name": "Format Test",
        "email": "formattest@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    response = client.post("/api/users/login", json={
        "email": "formattest@example.com",
        "password": "not-valid-base64!!!"
    })
    assert response.status_code == 400


def test_sprint_end_date_before_start_date_rejected(client):
    """end_date earlier than start_date should be rejected"""
    token = get_admin_token(client)
    project = client.post("/api/projects/", json={
        "name": "Date Validation Project",
        "description": "test",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    project_id = project.json()["id"]

    response = client.post("/api/sprints/", json={
        "name": "Bad Dates Sprint",
        "project_id": project_id,
        "goal": "test",
        "start_date": "2026-08-10",
        "end_date": "2026-08-01"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_pagination_limit_respected(client):
    """limit param should cap the number of results returned"""
    token = get_admin_token(client)
    response = client.get("/api/users/?limit=1",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) <= 1