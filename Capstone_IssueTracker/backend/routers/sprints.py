from fastapi import APIRouter, Depends
from schemas.sprint_schema import SprintCreate, SprintResponse, SprintUpdate, SprintStatusUpdate
from services.sprint_service import (
    create_sprint, get_sprints_by_project, add_issue_to_sprint,
    remove_issue_from_sprint, update_sprint_details, update_sprint_status, delete_sprint)
from utils.dependencies import get_current_user, require_admin
from services.sprint_service import get_active_sprint_count

router = APIRouter(
    prefix="/api/sprints",
    tags=["Sprints"]
)

@router.post("/", response_model=SprintResponse)
def create_new_sprint(sprint: SprintCreate, current_user: dict = Depends(require_admin)):
    return create_sprint(
        name=sprint.name,
        project_id=sprint.project_id,
        goal=sprint.goal,
        start_date=sprint.start_date,
        end_date=sprint.end_date
    )

@router.get("/project/{project_id}")
def list_sprints(project_id: str, current_user: dict = Depends(get_current_user)):
    return get_sprints_by_project(project_id)

@router.get("/active-count")
def active_sprint_count(current_user: dict = Depends(get_current_user)):
    return {"active_sprints": get_active_sprint_count()}

@router.post("/{sprint_id}/issues/{issue_id}")
def add_issue(sprint_id: str, issue_id: str, current_user: dict = Depends(get_current_user)):
    return add_issue_to_sprint(sprint_id, issue_id)

@router.delete("/{sprint_id}/issues/{issue_id}")
def remove_issue(sprint_id: str, issue_id: str, current_user: dict = Depends(get_current_user)):
    return remove_issue_from_sprint(sprint_id, issue_id)

@router.patch("/{sprint_id}/status", response_model=SprintResponse)
def change_sprint_status(sprint_id: str, body: SprintStatusUpdate, current_user: dict = Depends(require_admin)):
    return update_sprint_status(sprint_id, body.status.value)

@router.patch("/{sprint_id}", response_model=SprintResponse)
def edit_sprint(sprint_id: str, body: SprintUpdate, current_user: dict = Depends(require_admin)):
    return update_sprint_details(sprint_id, body.name, body.goal)

@router.delete("/{sprint_id}")
def remove_sprint(sprint_id: str, current_user: dict = Depends(require_admin)):
    return delete_sprint(sprint_id)