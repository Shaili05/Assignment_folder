from fastapi import HTTPException
from database import db
from models.issue_model import issue_helper, create_issue_document
from bson import ObjectId

issues_collection = db["issues"]
projects_collection = db["projects"]

def create_issue(title: str, description: str, issue_type: str,
                 priority: str, project_id: str,
                 assignee_id: str, created_by: str):
    # Validate project exists
    try:
        project = projects_collection.find_one({"_id": ObjectId(project_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id format")
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    issue_doc = create_issue_document(
        title, description, issue_type,
        priority, project_id, assignee_id, created_by
    )
    result = issues_collection.insert_one(issue_doc)
    new_issue = issues_collection.find_one({"_id": result.inserted_id})
    return issue_helper(new_issue)

def get_issues_by_project(project_id: str):
    issues = issues_collection.find({"project_id": project_id})
    return [issue_helper(i) for i in issues]

def get_issue_by_id(issue_id: str):
    try:
        issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid issue_id format")
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue_helper(issue)