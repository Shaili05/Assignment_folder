# Projects router - defines all project API endpoints
from fastapi import APIRouter, Depends
from services.project_service import (
    create_project, get_all_projects, add_member, remove_member,
    get_project_members, get_project_by_id, update_project_description, delete_project)
from schemas.project_schema import ProjectCreate, ProjectResponse, ProjectDescriptionUpdate
from utils.dependencies import require_admin, get_current_user


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

@router.post("/", response_model=ProjectResponse)
def create_new_project(project: ProjectCreate, current_user: dict = Depends(require_admin)):
    """Create a project - admin only"""
    return create_project(project, owner_id=current_user.get("user_id"))


@router.get("/")
def list_projects(skip: int = 0, limit: int = 0, current_user: dict = Depends(get_current_user)):
    """Get projects - admin sees all, member/viewer see only assigned ones. Optional pagination."""
    return get_all_projects(current_user, skip, limit)

@router.post("/{project_id}/members/{user_id}")
def add_project_member(project_id: str, user_id: str, current_user: dict = Depends(require_admin)):
    """Add member to project - admin only"""
    return add_member(project_id, user_id)

@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(project_id: str, user_id: str, current_user: dict = Depends(require_admin)):
    """Remove member from project - admin only"""
    return remove_member(project_id, user_id)

@router.get("/{project_id}/members")
def list_project_members(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get resolved member details for a project"""
    return get_project_members(project_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get single project detail"""
    return get_project_by_id(project_id)

@router.patch("/{project_id}", response_model=ProjectResponse)
def edit_project(project_id: str, body: ProjectDescriptionUpdate, current_user: dict = Depends(require_admin)):
    """Admin edits project description only. Name and key are immutable."""
    return update_project_description(project_id, body.description)

@router.delete("/{project_id}")
def remove_project(project_id: str, current_user: dict = Depends(require_admin)):
    """Admin deletes a project (cascades to its issues and sprints)"""
    return delete_project(project_id)