from fastapi import APIRouter, Depends
from schemas.issue_schema import IssueCreate, IssueResponse
from services.issue_service import create_issue, get_issues_by_project, get_issue_by_id
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/api/issues",
    tags=["Issues"]
)

@router.post("/", response_model=IssueResponse)
def create_new_issue(issue: IssueCreate, current_user: dict = Depends(get_current_user)):
    return create_issue(
        title=issue.title,
        description=issue.description,
        issue_type=issue.issue_type.value,
        priority=issue.priority.value,
        project_id=issue.project_id,
        assignee_id=issue.assignee_id,
        created_by=current_user.get("user_id")
    )

@router.get("/project/{project_id}")
def list_issues(project_id: str, current_user: dict = Depends(get_current_user)):
    return get_issues_by_project(project_id)

@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: str, current_user: dict = Depends(get_current_user)):
    return get_issue_by_id(issue_id)

from services.issue_service import create_issue, get_issues_by_project, get_issue_by_id, update_issue_status
from pydantic import BaseModel

class StatusUpdate(BaseModel):
    status: str

@router.patch("/{issue_id}/status", response_model=IssueResponse)
def update_status(issue_id: str, body: StatusUpdate, current_user: dict = Depends(get_current_user)):
    return update_issue_status(
        issue_id=issue_id,
        new_status=body.status,
        current_user_id=current_user.get("user_id")
    )