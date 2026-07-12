import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def setup_issue(client):
    """Helper: create admin, project, issue — returns (token, issue_id)"""
    client.post("/api/users/register", json={
        "name": "Workflow Admin",
        "email": "workflowadmin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    login = client.post("/api/users/login", json={
        "email": "workflowadmin@example.com",
        "password": b64("Test@123")
    })
    token = login.json()["access_token"]
    user_id = login.json().get("user_id")

    project = client.post("/api/projects/", json={
        "name": "Workflow Project",
        "description": "For workflow tests",
        "project_key": "WFP",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    project_id = project.json()["id"]

    # Get user_id from /me endpoint
    me = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me.json()["user_id"]

    issue = client.post("/api/issues/", json={
        "title": "Workflow Test Issue",
        "description": "Testing transitions",
        "issue_type": "task",
        "priority": "medium",
        "project_id": project_id,
        "assignee_id": user_id
    }, headers={"Authorization": f"Bearer {token}"})
    issue_id = issue.json()["id"]

    return token, issue_id

def test_valid_status_transition(client):
    """BACKLOG → TODO should succeed"""
    token, issue_id = setup_issue(client)
    response = client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "TODO"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "TODO"

def test_invalid_status_transition(client):
    """BACKLOG → DONE directly should return 409"""
    token, issue_id = setup_issue(client)
    response = client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "DONE"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409

def test_non_assignee_cannot_update_status(client):
    """A different user should not be able to update status — returns 403"""
    token, issue_id = setup_issue(client)

    # Register a second user
    client.post("/api/users/register", json={
        "name": "Other User",
        "email": "otheruser@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    other_login = client.post("/api/users/login", json={
        "email": "otheruser@example.com",
        "password": b64("Test@123")
    })
    other_token = other_login.json()["access_token"]

    response = client.patch(
        f"/api/issues/{issue_id}/status",
        json={"status": "TODO"},
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert response.status_code == 403