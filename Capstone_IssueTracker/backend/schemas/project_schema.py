# Project schema - defines what data is accepted for project requests
from pydantic import BaseModel
from typing import List, Optional

class ProjectCreate(BaseModel):
    name: str
    description: str
    project_key: str
    members: Optional[List[str]] = []

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    project_key: str
    members: List[str]
    owner_id: str