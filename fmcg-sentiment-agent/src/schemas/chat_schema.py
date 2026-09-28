from typing import Optional
from pydantic import BaseModel

class AssistantQuery(BaseModel):
    question: str
    role: str = "brand_manager"
    session_id: Optional[str] = None
    model: Optional[str] = None
