import base64

def b64(password: str) -> str:
    return base64.b64encode(password.encode()).decode()

def get_admin_token(client):
    client.post("/api/users/register", json={
        "name": "Comment Admin",
        "email": "commentadmin@example.com",
        "password": b64("Test@123"),
        "role": "admin"
    })
    response = client.post("/api/users/login", json={
        "email": "commentadmin@example.com",
        "password": b64("Test@123")
    })
    return response.json()["access_token"]

def create_test_project(client, token):
    response = client.post("/api/projects/", json={
        "name": "Comment Test Project",
        "description": "For comment tests",
        "project_key": "CTP",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]

def create_test_issue(client, token, project_id):
    response = client.post("/api/issues/", json={
        "title": "Comment Test Issue",
        "description": "For comment tests",
        "issue_type": "task",
        "priority": "medium",
        "project_id": project_id
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]

def test_add_comment(client):
    """Should be able to add a comment to an issue"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    response = client.post(
        f"/api/issues/{issue_id}/comments",
        json={"content": "This looks good to me"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == "This looks good to me"

def test_get_comments_for_issue(client):
    """Should retrieve all comments for an issue in order"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    client.post(f"/api/issues/{issue_id}/comments", json={"content": "First comment"},
        headers={"Authorization": f"Bearer {token}"})
    client.post(f"/api/issues/{issue_id}/comments", json={"content": "Second comment"},
        headers={"Authorization": f"Bearer {token}"})

    response = client.get(f"/api/issues/{issue_id}/comments",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 2
    assert comments[0]["content"] == "First comment"

def test_edit_own_comment(client):
    """User should be able to edit their own comment"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    create_response = client.post(f"/api/issues/{issue_id}/comments", json={"content": "Original text"},
        headers={"Authorization": f"Bearer {token}"})
    comment_id = create_response.json()["id"]

    response = client.patch(f"/api/issues/comments/{comment_id}", json={"content": "Edited text"},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["content"] == "Edited text"

def test_delete_own_comment(client):
    """User should be able to delete their own comment"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    create_response = client.post(f"/api/issues/{issue_id}/comments", json={"content": "To be deleted"},
        headers={"Authorization": f"Bearer {token}"})
    comment_id = create_response.json()["id"]

    response = client.delete(f"/api/issues/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    get_response = client.get(f"/api/issues/{issue_id}/comments",
        headers={"Authorization": f"Bearer {token}"})
    assert get_response.json() == []

def test_non_author_cannot_edit_comment(client):
    """A different user should not be able to edit someone else's comment"""
    token = get_admin_token(client)
    project_id = create_test_project(client, token)
    issue_id = create_test_issue(client, token, project_id)

    create_response = client.post(f"/api/issues/{issue_id}/comments", json={"content": "Original"},
        headers={"Authorization": f"Bearer {token}"})
    comment_id = create_response.json()["id"]

    client.post("/api/users/register", json={
        "name": "Other User",
        "email": "othercommentuser@example.com",
        "password": b64("Test@123"),
        "role": "member"
    })
    other_login = client.post("/api/users/login", json={
        "email": "othercommentuser@example.com",
        "password": b64("Test@123")
    })
    other_token = other_login.json()["access_token"]

    response = client.patch(f"/api/issues/comments/{comment_id}", json={"content": "Hacked"},
        headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 403