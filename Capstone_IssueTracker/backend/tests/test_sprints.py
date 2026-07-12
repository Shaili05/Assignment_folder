import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def get_admin_token(client):
    client.post("/api/users/register", json={
        "name": "Sprint Admin",
        "email": "sprintadmin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    response = client.post("/api/users/login", json={
        "email": "sprintadmin@example.com",
        "password": b64("Test@123")
    })
    return response.json()["access_token"]

def create_test_project(client, token):
    response = client.post("/api/projects/", json={
        "name": "Sprint Test Project",
        "description": "For sprint tests",
        "project_key": "STP",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]

def create_test_issue(client, token, project_id):
    response = client.post("/api/issues/", json={
        "title": "Sprint Test Issue",
        "description": "For sprint tests",
        "issue_type": "task",
        "priority": "medium",
        "project_id": project_id
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]

def test_create_sprint(client):
    """Admin should be able to create a sprint"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    response = client.post("/api/sprints/", json={
        "name": "Sprint 1",
        "project_id": project_id,
        "goal": "Complete user module",
        "start_date": "2026-07-01",
        "end_date": "2026-07-14"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Sprint 1"
    assert response.json()["status"] == "planned"

def test_add_issue_to_sprint(client):
    """Should be able to add an issue to a sprint"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)
    sprint_response = client.post("/api/sprints/", json={
        "name": "Sprint 2",
        "project_id": project_id,
        "goal": "Fix bugs",
        "start_date": "2026-07-01",
        "end_date": "2026-07-14"
    }, headers={"Authorization": f"Bearer {token}"})
    sprint_id = sprint_response.json()["id"]

    response = client.post(
        f"/api/sprints/{sprint_id}/issues/{issue_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert issue_id in response.json()["issues"]

def test_prevent_adding_done_issue(client):
    """Should not be able to add a DONE issue to a sprint"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    # Get the admin's user_id from /me so we can self-assign
    me_response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    admin_user_id = me_response.json()["user_id"]

    # Assign the issue to admin so status updates are permitted
    client.patch(f"/api/issues/{issue_id}/assign",
        json={"assignee_id": admin_user_id}, headers={"Authorization": f"Bearer {token}"})

    # Move issue to DONE through all transitions
    client.patch(f"/api/issues/{issue_id}/status",
        json={"status": "TODO"}, headers={"Authorization": f"Bearer {token}"})
    client.patch(f"/api/issues/{issue_id}/status",
        json={"status": "IN_PROGRESS"}, headers={"Authorization": f"Bearer {token}"})
    client.patch(f"/api/issues/{issue_id}/status",
        json={"status": "DONE"}, headers={"Authorization": f"Bearer {token}"})

    sprint_response = client.post("/api/sprints/", json={
        "name": "Sprint 3",
        "project_id": project_id,
        "goal": "Testing",
        "start_date": "2026-07-01",
        "end_date": "2026-07-14"
    }, headers={"Authorization": f"Bearer {token}"})
    sprint_id = sprint_response.json()["id"]

    response = client.post(
        f"/api/sprints/{sprint_id}/issues/{issue_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409