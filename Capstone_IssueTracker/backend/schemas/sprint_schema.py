from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import date


class SprintStatus(str, Enum):
    planned = "planned"
    active = "active"
    completed = "completed"


class SprintCreate(BaseModel):
    name: str
    project_id: str
    goal: Optional[str] = ""
    start_date: date
    end_date: date
    status: SprintStatus = SprintStatus.planned


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SprintStatusUpdate(BaseModel):
    status: SprintStatus


class SprintResponse(BaseModel):
    id: str
    name: str
    project_id: str
    goal: Optional[str] = ""
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    issues: List[str] = []