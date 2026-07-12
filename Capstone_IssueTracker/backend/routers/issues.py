from fastapi import APIRouter, Depends
from schemas.issue_schema import IssueCreate, IssueResponse, AssigneeUpdate, IssueUpdate
from services.issue_service import (
    create_issue, get_issues_by_project, get_issue_by_id,
    update_issue_status, get_my_issues, reassign_issue,
    update_issue_details, delete_issue)
from utils.dependencies import get_current_user, require_admin
from services.issue_service import get_assigned_counts_by_user
from services.issue_service import get_issue_stats
from services.issue_service import get_issues_filtered
from pydantic import BaseModel

router = APIRouter(prefix="/api/issues", tags=["Issues"])

class StatusUpdate(BaseModel):
    status: str

@router.post("/", response_model=IssueResponse)
def create_new_issue(issue: IssueCreate, current_user: dict = Depends(get_current_user)):
    return create_issue(
        title=issue.title,
        description=issue.description,
        issue_type=issue.issue_type.value,
        priority=issue.priority.value,
        project_id=issue.project_id,
        assignee_id=issue.assignee_id,
        created_by=current_user.get("user_id"),
        parent_id=issue.parent_id
    )


@router.get("/")
def list_all_issues(
    project_id: str = None,
    search: str = None,
    status: str = None,
    assignee_id: str = None,
    skip: int = 0,
    limit: int = 0,
    current_user: dict = Depends(get_current_user)
):
    return get_issues_filtered(current_user, project_id, search, status, assignee_id, skip, limit)
    

@router.get("/my-issues")
def list_my_issues(current_user: dict = Depends(get_current_user)):
    return get_my_issues(current_user.get("user_id"))

@router.get("/assigned-counts")
def assigned_counts(current_user: dict = Depends(require_admin)):
    return get_assigned_counts_by_user()

@router.get("/stats")
def issue_stats(current_user: dict = Depends(get_current_user)):
    return get_issue_stats()

@router.get("/project/{project_id}")
def list_issues(
    project_id: str,
    search: str = None,
    status: str = None,
    assignee_id: str = None,
    current_user: dict = Depends(get_current_user)
):
    return get_issues_by_project(project_id, search, status, assignee_id)


@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: str, current_user: dict = Depends(get_current_user)):
    return get_issue_by_id(issue_id)

@router.patch("/{issue_id}/status", response_model=IssueResponse)
def update_status(issue_id: str, body: StatusUpdate, current_user: dict = Depends(get_current_user)):
    return update_issue_status(
        issue_id=issue_id,
        new_status=body.status,
        current_user_id=current_user.get("user_id"),
        current_user_role=current_user.get("role")
    )

@router.patch("/{issue_id}/assign", response_model=IssueResponse)
def assign_issue(issue_id: str, body: AssigneeUpdate, current_user: dict = Depends(require_admin)):
    """Admin reassigns an issue to a different user."""
    return reassign_issue(issue_id, body.assignee_id)

@router.patch("/{issue_id}", response_model=IssueResponse)
def edit_issue(issue_id: str, body: IssueUpdate, current_user: dict = Depends(require_admin)):
    """Admin edits issue description/priority/type. Title is immutable."""
    return update_issue_details(issue_id, body.description, body.priority, body.issue_type)

@router.delete("/{issue_id}")
def remove_issue(issue_id: str, current_user: dict = Depends(require_admin)):
    """Admin deletes an issue"""
    return delete_issue(issue_id)