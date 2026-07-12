from fastapi import HTTPException
from database import db
from models.issue_model import issue_helper, create_issue_document
from bson import ObjectId

issues_collection = db["issues"]
projects_collection = db["projects"]

def create_issue(title: str, description: str, issue_type: str,
                 priority: str, project_id: str,
                 assignee_id: str, created_by: str, parent_id: str = None):
    # Validate project exists
    try:
        project = projects_collection.find_one({"_id": ObjectId(project_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validate parent issue if provided
    if parent_id:
        try:
            parent = issues_collection.find_one({"_id": ObjectId(parent_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid parent_id format")

        if not parent:
            raise HTTPException(status_code=404, detail="Parent issue does not exist")
        if parent.get("issue_type") != "story":
            raise HTTPException(status_code=400, detail="parent_id must reference a Story")
        if parent.get("project_id") != project_id:
            raise HTTPException(status_code=400, detail="Parent issue must belong to the same project")

    issue_doc = create_issue_document(
        title, description, issue_type,
        priority, project_id, assignee_id, created_by, parent_id
    )
    result = issues_collection.insert_one(issue_doc)
    new_issue = issues_collection.find_one({"_id": result.inserted_id})
    return issue_helper(new_issue)

def get_issues_by_project(project_id: str, search: str = None, status: str = None, assignee_id: str = None):
    query = {"project_id": project_id}
    if status:
        query["status"] = status
    if assignee_id:
        query["assignee_id"] = assignee_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    issues = issues_collection.find(query)
    return [issue_helper(i) for i in issues]


def get_issue_by_id(issue_id: str):
    try:
        issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue_helper(issue)


VALID_TRANSITIONS = {
    "BACKLOG": ["TODO"],
    "TODO": ["IN_PROGRESS"],
    "IN_PROGRESS": ["DONE"],
    "DONE": []
}

def update_issue_status(issue_id: str, new_status: str, current_user_id: str, current_user_role: str):
    issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Admin can always override; otherwise must be the assignee
    if current_user_role != "admin" and issue.get("assignee_id") != current_user_id:
        raise HTTPException(status_code=403, detail="Only the assignee or an admin can update status")

    current_status = issue.get("status")

    if new_status not in VALID_TRANSITIONS.get(current_status, []):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot move from {current_status} to {new_status}"
        )

    issues_collection.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": {"status": new_status}}
    )
    updated = issues_collection.find_one({"_id": ObjectId(issue_id)})
    return issue_helper(updated)


def get_my_issues(user_id: str):
    """Return all issues currently assigned to this user, regardless of project."""
    issues = issues_collection.find({"assignee_id": user_id})
    return [issue_helper(i) for i in issues]

def reassign_issue(issue_id: str, new_assignee_id: str):
    """Admin reassigns an issue to a different user. No status-transition rules apply here —
    this changes WHO owns it, not its workflow state."""
    try:
        issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issues_collection.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": {"assignee_id": new_assignee_id}}
    )
    updated = issues_collection.find_one({"_id": ObjectId(issue_id)})
    return issue_helper(updated)

def update_issue_details(issue_id: str, description: str, priority: str, issue_type: str):
    """Admin edits description/priority/type. Title is immutable after creation."""
    try:
        result = issues_collection.update_one(
            {"_id": ObjectId(issue_id)},
            {"$set": {"description": description, "priority": priority, "issue_type": issue_type}}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")

    updated = issues_collection.find_one({"_id": ObjectId(issue_id)})
    return issue_helper(updated)

def delete_issue(issue_id: str):
    """Admin deletes an issue permanently."""
    try:
        result = issues_collection.delete_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Issue not found")

    return {"message": "Issue deleted successfully"}


def get_assigned_counts_by_user():
    """Returns a dict mapping user_id -> count of currently assigned issues (not DONE)."""
    pipeline = [
        {"$match": {"assignee_id": {"$ne": None}, "status": {"$ne": "DONE"}}},
        {"$group": {"_id": "$assignee_id", "count": {"$sum": 1}}}
    ]
    results = issues_collection.aggregate(pipeline)
    return {r["_id"]: r["count"] for r in results}

def get_issue_stats():
    """Returns total issue count and open (non-DONE) issue count across all projects."""
    total = issues_collection.count_documents({})
    open_count = issues_collection.count_documents({"status": {"$ne": "DONE"}})
    return {"total_issues": total, "open_issues": open_count}


def get_issues_filtered(current_user, project_id=None, search=None, status=None, assignee_id=None, skip: int = 0, limit: int = 0):
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

    if status:
        query["status"] = status
    if assignee_id:
        query["assignee_id"] = assignee_id
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    cursor = issues_collection.find(query).skip(skip)
    if limit > 0:
        cursor = cursor.limit(limit)
    return [issue_helper(i) for i in cursor]