from pydantic import BaseModel
from typing import Optional
from enum import Enum

class IssueType(str, Enum):
    bug = "bug"
    task = "task"
    story = "story"

class IssuePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class IssueStatus(str, Enum):
    backlog = "BACKLOG"
    todo = "TODO"
    in_progress = "IN_PROGRESS"
    done = "DONE"

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    issue_type: IssueType = IssueType.task
    priority: IssuePriority = IssuePriority.medium
    project_id: str
    assignee_id: Optional[str] = None

class IssueResponse(BaseModel):
    id: str
    title: str
    description: str
    issue_type: str
    priority: str
    status: str
    project_id: str
    assignee_id: Optional[str]
    created_by: str