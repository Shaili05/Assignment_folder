# Projects router - defines all project API endpoints
from fastapi import APIRouter, Depends
from schemas.project_schema import ProjectCreate, ProjectResponse
from services.project_service import create_project, get_all_projects, add_member, remove_member
from utils.dependencies import require_admin, get_current_user

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)

@router.post("/", response_model=ProjectResponse)
def create_new_project(project: ProjectCreate, current_user: dict = Depends(require_admin)):
    """Create a project - admin only"""
    return create_project(
        name=project.name,
        description=project.description,
        project_key=project.project_key,
        members=project.members,
        owner_id=current_user.get("user_id")
    )

@router.get("/")
def list_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects - any logged in user"""
    return get_all_projects()

@router.post("/{project_id}/members/{user_id}")
def add_project_member(project_id: str, user_id: str, current_user: dict = Depends(require_admin)):
    """Add member to project - admin only"""
    return add_member(project_id, user_id)

@router.delete("/{project_id}/members/{user_id}")
def remove_project_member(project_id: str, user_id: str, current_user: dict = Depends(require_admin)):
    """Remove member from project - admin only"""
    return remove_member(project_id, user_id)