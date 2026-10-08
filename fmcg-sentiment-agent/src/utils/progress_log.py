import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.callbacks import AsyncCallbackHandler

from src.config.constants import (
    STAGE_MODEL_CALL, STAGE_QUESTION_RECEIVED, STAGE_TOOL_DONE, STAGE_TOOL_FAILED, STAGE_TOOL_START,
)
from src.config.settings import PROGRESS_LOG_PATH

logger = logging.getLogger(__name__)


def log_stage(session_id, role, stage, detail="", path=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": session_id,
        "role": role,
        "stage": stage,
        "detail": detail,
    }
    target = Path(path or PROGRESS_LOG_PATH)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        logger.exception("Could not write progress stage %s", stage)
    return entry


def read_progress(session_id, path=None):
    target = Path(path or PROGRESS_LOG_PATH)
    if not target.exists():
        return []
    stages = []
    with target.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("session_id") != session_id:
                continue
            if entry.get("stage") == STAGE_QUESTION_RECEIVED:
                stages = []
            stages.append(entry)
    return stages


class StageCallback(AsyncCallbackHandler):

    def __init__(self, session_id, role, path=None):
        super().__init__()
        self.session_id = session_id
        self.role = role
        self.path = path
        self.model_calls = 0
        self.running_tools = {}

    def record(self, stage, detail):
        log_stage(self.session_id, self.role, stage, detail, self.path)

    async def on_chat_model_start(self, serialized, messages, **kwargs):
        self.model_calls += 1
        self.record(STAGE_MODEL_CALL, f"model call {self.model_calls}")

    async def on_tool_start(self, serialized, input_str, **kwargs):
        name = kwargs.get("name") or (serialized or {}).get("name", "")
        self.running_tools[kwargs.get("run_id")] = (name, time.monotonic())
        self.record(STAGE_TOOL_START, name)

    async def on_tool_end(self, output, **kwargs):
        name, started = self.running_tools.pop(kwargs.get("run_id"), ("", time.monotonic()))
        self.record(STAGE_TOOL_DONE, f"{name} ({time.monotonic() - started:.1f} s)")

    async def on_tool_error(self, error, **kwargs):
        name, _ = self.running_tools.pop(kwargs.get("run_id"), ("", 0))
        self.record(STAGE_TOOL_FAILED, f"{name}: {error.__class__.__name__}")
