from fastapi import HTTPException
from database import db
from models.sprint_model import sprint_helper, create_sprint_document
from bson import ObjectId

sprints_collection = db["sprints"]
issues_collection = db["issues"]
projects_collection = db["projects"]

def create_sprint(name: str, project_id: str, goal: str, start_date, end_date, status: str = "planned"):
    try:
        project = projects_collection.find_one({"_id": ObjectId(project_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")

    if status == "active":
        existing_active = sprints_collection.find_one({"project_id": project_id, "status": "active"})
        if existing_active:
            raise HTTPException(status_code=409, detail="Another sprint is already active in this project")

    sprint_doc = create_sprint_document(
        name, project_id, goal,
        start_date.isoformat(), end_date.isoformat()
    )
    sprint_doc["status"] = status
    result = sprints_collection.insert_one(sprint_doc)
    new_sprint = sprints_collection.find_one({"_id": result.inserted_id})
    return sprint_helper(new_sprint)

def get_sprints_by_project(project_id: str):
    sprints = sprints_collection.find({"project_id": project_id})
    return [sprint_helper(s) for s in sprints]

def add_issue_to_sprint(sprint_id: str, issue_id: str):
    try:
        sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
        issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")

    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue["status"] == "DONE":
        raise HTTPException(status_code=409, detail="Cannot add a DONE issue to a sprint")

    sprints_collection.update_one(
        {"_id": ObjectId(sprint_id)},
        {"$addToSet": {"issues": issue_id}}
    )
    updated = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    return sprint_helper(updated)

def remove_issue_from_sprint(sprint_id: str, issue_id: str):
    try:
        sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid sprint_id format")
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    sprints_collection.update_one(
        {"_id": ObjectId(sprint_id)},
        {"$pull": {"issues": issue_id}}
    )
    updated = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    return sprint_helper(updated)

def update_sprint_details(sprint_id: str, name: str, goal: str, start_date=None, end_date=None):
    update_fields = {}
    if name is not None:
        update_fields["name"] = name
    if goal is not None:
        update_fields["goal"] = goal
    if start_date is not None:
        update_fields["start_date"] = start_date.isoformat()
    if end_date is not None:
        update_fields["end_date"] = end_date.isoformat()

    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date cannot be before start_date")

    try:
        result = sprints_collection.update_one(
            {"_id": ObjectId(sprint_id)},
            {"$set": update_fields}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid sprint_id format")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sprint not found")
    updated = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    return sprint_helper(updated)


def update_sprint_status(sprint_id: str, new_status: str):
    try:
        sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid sprint_id format")
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    if new_status == "active":
        existing_active = sprints_collection.find_one({
            "project_id": sprint["project_id"],
            "status": "active",
            "_id": {"$ne": ObjectId(sprint_id)}
        })
        if existing_active:
            raise HTTPException(
                status_code=409,
                detail="Another sprint is already active in this project"
            )

    sprints_collection.update_one(
        {"_id": ObjectId(sprint_id)},
        {"$set": {"status": new_status}}
    )
    updated = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    return sprint_helper(updated)

def delete_sprint(sprint_id: str):
    sprint = sprints_collection.find_one({"_id": ObjectId(sprint_id)})
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    issue_ids = sprint.get("issues", [])
    if issue_ids:
        incomplete = issues_collection.find_one({
            "_id": {"$in": [ObjectId(i) for i in issue_ids]},
            "status": {"$ne": "DONE"}
        })
        if incomplete:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete sprint: it has incomplete issues. Move or complete them first."
            )

    sprints_collection.delete_one({"_id": ObjectId(sprint_id)})
    return {"message": "Sprint deleted"}


def get_active_sprint_count():
    """Returns count of currently active sprints across all projects."""
    return sprints_collection.count_documents({"status": "active"})


def get_sprints_filtered(current_user, project_id=None):
    from services.project_service import get_all_projects
    accessible = get_all_projects(current_user)
    accessible_ids = [p["id"] for p in accessible]

    if project_id:
        if project_id not in accessible_ids:
            raise HTTPException(status_code=403, detail="No access to this project")
        query = {"project_id": project_id}
    else:
        if not accessible_ids:
            return []
        query = {"project_id": {"$in": accessible_ids}}

    sprints = sprints_collection.find(query)
    return [sprint_helper(s) for s in sprints]