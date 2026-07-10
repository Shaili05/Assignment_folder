# Project service - business logic for project operations
from fastapi import HTTPException
from database import db
from models.project_model import project_helper, create_project_document
from bson import ObjectId
from schemas.project_schema import ProjectCreate

projects_collection = db["projects"]
issues_collection = db["issues"]
sprints_collection = db["sprints"]


def generate_project_key(name: str) -> str:
    """Auto-generate a short project key from the project name."""
    words = [w for w in name.strip().split() if w]
    if len(words) >= 2:
        key = "".join(w[0] for w in words[:4]).upper()
    else:
        key = (name.strip()[:4] or "PRJ").upper()

    base_key = key
    counter = 1
    while projects_collection.find_one({"project_key": key}):
        counter += 1
        key = f"{base_key}{counter}"
    return key


def create_project(payload: ProjectCreate, owner_id: str):
    """Create a new project - only admin can do this. project_key is auto-generated."""
    existing_name = projects_collection.find_one({"name": payload.name})
    if existing_name:
        raise HTTPException(status_code=409, detail="A project with this name already exists")

    project_key = generate_project_key(payload.name)
    project_doc = create_project_document(payload.name, payload.description, project_key, payload.members, owner_id)
    result = projects_collection.insert_one(project_doc)
    new_project = projects_collection.find_one({"_id": result.inserted_id})
    return project_helper(new_project)


def get_all_projects(current_user: dict):
    """Admin and Viewer see all projects. Member sees only projects they belong to."""
    role = current_user.get("role")
    if role in ("admin", "viewer"):
        projects = projects_collection.find()
    else:
        user_id = current_user.get("user_id")
        projects = projects_collection.find({"members": user_id})
    return [project_helper(p) for p in projects]


def get_project_members(project_id: str):
    """Resolve member user IDs into full user info for display"""
    from database import users_collection
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    member_ids = project.get("members", [])
    members = []
    for mid in member_ids:
        try:
            u = users_collection.find_one({"_id": ObjectId(mid)})
            if u:
                members.append({"id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u["role"]})
        except Exception:
            continue
    return members


def add_member(project_id: str, user_id: str):
    """Add a member to a project"""
    result = projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$addToSet": {"members": user_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Member added successfully"}


def remove_member(project_id: str, user_id: str):
    """Remove a member from a project"""
    result = projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$pull": {"members": user_id}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Member removed successfully"}


def get_project_by_id(project_id: str):
    """Get full detail for one project"""
    try:
        project = projects_collection.find_one({"_id": ObjectId(project_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_helper(project)


def update_project_description(project_id: str, description: str):
    """Admin can update ONLY the description. Name and project_key are immutable after creation."""
    try:
        result = projects_collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"description": description}}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = projects_collection.find_one({"_id": ObjectId(project_id)})
    return project_helper(updated)


def delete_project(project_id: str):
    project = projects_collection.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    incomplete = issues_collection.find_one({
        "project_id": project_id,
        "status": {"$ne": "DONE"}
    })
    if incomplete:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete project: it has incomplete issues. Resolve them first."
        )

    issues_collection.delete_many({"project_id": project_id})
    sprints_collection.delete_many({"project_id": project_id})
    projects_collection.delete_one({"_id": ObjectId(project_id)})
    return {"message": "Project deleted"}