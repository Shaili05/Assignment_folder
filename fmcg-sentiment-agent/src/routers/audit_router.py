from fastapi import APIRouter

from src.agents.audit import read_log

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs")
def get_logs(role: str = "brand_manager", session_id: str = None):
    return read_log(role, session_id=session_id)
