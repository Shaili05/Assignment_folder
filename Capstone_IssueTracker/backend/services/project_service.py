# Project service - business logic for project operations
from fastapi import HTTPException
from database import db
from models.project_model import project_helper, create_project_document
from bson import ObjectId

projects_collection = db["projects"]

def create_project(name: str, description: str, project_key: str, members: list, owner_id: str):
    """Create a new project - only admin can do this"""
    existing = projects_collection.find_one({"project_key": project_key})
    if existing:
        raise HTTPException(status_code=409, detail="Project key already exists")
    
    project_doc = create_project_document(name, description, project_key, members, owner_id)
    result = projects_collection.insert_one(project_doc)
    new_project = projects_collection.find_one({"_id": result.inserted_id})
    return project_helper(new_project)

def get_all_projects():
    """Get all projects"""
    projects = projects_collection.find()
    return [project_helper(p) for p in projects]

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