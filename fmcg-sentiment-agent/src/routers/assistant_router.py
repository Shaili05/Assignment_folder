from fastapi import APIRouter

from src.schemas.chat_schema import AssistantQuery
from src.schemas.response_schema import AssistantResponse
from src.services.agent_service import ask_assistant, get_status as get_assistant_status

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("", response_model=AssistantResponse)
def post_question(payload: AssistantQuery):
    return ask_assistant(payload.question, payload.role, payload.session_id, payload.model)


@router.get("/status")
def status(model: str = None):
    return get_assistant_status(model)


