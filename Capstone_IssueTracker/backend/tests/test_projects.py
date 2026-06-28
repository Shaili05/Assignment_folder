import pytest

def get_admin_token(client):
    """Helper to register and login as admin, returns token"""
    client.post("/api/users/register", json={
        "name": "Admin User",
        "email": "projectadmin@example.com",
        "password": "Test@123",
        "role": "admin"
    })
    response = client.post("/api/users/login", json={
        "email": "projectadmin@example.com",
        "password": "Test@123"
    })
    return response.json()["access_token"]

def get_member_token(client):
    """Helper to register and login as member, returns token"""
    client.post("/api/users/register", json={
        "name": "Member User",
        "email": "projectmember@example.com",
        "password": "Test@123",
        "role": "member"
    })
    response = client.post("/api/users/login", json={
        "email": "projectmember@example.com",
        "password": "Test@123"
    })
    return response.json()["access_token"]

# Test 1: Admin can create a project
def test_create_project_as_admin(client):
    """Admin should be able to create a project"""
    token = get_admin_token(client)
    response = client.post("/api/projects/", json={
        "name": "Test Project",
        "description": "A test project",
        "project_key": "TEST",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"

# Test 2: Member cannot create a project
def test_create_project_as_member(client):
    """Member should be blocked from creating a project"""
    token = get_member_token(client)
    response = client.post("/api/projects/", json={
        "name": "Test Project",
        "description": "A test project",
        "project_key": "TEST2",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

# Test 3: Admin can add a member to a project
def test_add_member_to_project(client):
    """Admin should be able to add a member to a project"""
    token = get_admin_token(client)
    # First create a project
    project_response = client.post("/api/projects/", json={
        "name": "Member Test Project",
        "description": "Testing member addition",
        "project_key": "MTP",
        "members": []
    }, headers={"Authorization": f"Bearer {token}"})
    project_id = project_response.json()["id"]
    
    # Add a member
    response = client.post(
        f"/api/projects/{project_id}/members/someuser123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200