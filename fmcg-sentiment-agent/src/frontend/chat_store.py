"""
chat_store.py
File-backed store for assistant conversations.


Every conversation is kept as one entry in logs/chat_sessions.json, keyed by
session id, so the dashboard can list past conversations, reopen them and
delete them. Tool outputs are dropped before saving: only the tool name and
its arguments are kept, which keeps the file small and avoids storing review
text twice (the audit log already holds the full record).


This store is for user convenience only. The append-only audit log in
src/agent/audit.py stays the system of record.
"""


import json
import threading
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STORE_PATH = REPO_ROOT / "logs" / "chat_sessions.json"

MAX_CONVERSATIONS = 50
TITLE_CHARS = 60

_LOCK = threading.Lock()


def _path(path=None):
    return Path(path or STORE_PATH)


def _read_all(path=None):
    target = _path(path)
    if not target.exists():
        return {}
    try:
        with target.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_all(data, path=None):
    target = _path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=str)


def _trim(data):
    if len(data) <= MAX_CONVERSATIONS:
        return data
    ordered = sorted(data.items(), key=lambda item: item[1].get("updated_at", ""), reverse=True)
    return dict(ordered[:MAX_CONVERSATIONS])


def make_title(messages):
    for message in messages:
        if message.get("role") == "user" and message.get("content"):
            text = " ".join(str(message["content"]).split())
            return text[:TITLE_CHARS] + ("..." if len(text) > TITLE_CHARS else "")
    return "New conversation"


def strip_message(message):
    """Keep the visible text and a light copy of the turn record."""
    record = message.get("record") or {}
    light_record = None
    if record:
        light_record = {
            "interaction_id": record.get("interaction_id"),
            "status": record.get("status"),
            "latency_sec": record.get("latency_sec"),
            "prompt_tokens": record.get("prompt_tokens"),
            "completion_tokens": record.get("completion_tokens"),
            "cost_usd": record.get("cost_usd"),
            "checks": record.get("checks") or {},
            "tool_calls": [
                {"name": call.get("name"), "arguments": call.get("arguments")}
                for call in record.get("tool_calls", [])
            ],
        }
    return {"role": message.get("role"), "content": message.get("content"), "record": light_record}


def save_conversation(session_id, role, messages, path=None):
    if not session_id or not messages:
        return
    with _LOCK:
        data = _read_all(path)
        data[session_id] = {
            "session_id": session_id,
            "role": role,
            "title": make_title(messages),
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "messages": [strip_message(m) for m in messages],
        }
        _write_all(_trim(data), path)


def list_conversations(role=None, path=None):
    data = _read_all(path)
    items = [entry for entry in data.values() if role is None or entry.get("role") == role]
    items.sort(key=lambda entry: entry.get("updated_at", ""), reverse=True)
    return [
        {
            "session_id": entry.get("session_id"),
            "title": entry.get("title", "Conversation"),
            "updated_at": entry.get("updated_at", ""),
            "message_count": len(entry.get("messages", [])),
        }
        for entry in items
    ]


def load_conversation(session_id, path=None):
    entry = _read_all(path).get(session_id)
    return list(entry.get("messages", [])) if entry else []


def delete_conversation(session_id, path=None):
    with _LOCK:
        data = _read_all(path)
        if session_id in data:
            del data[session_id]
            _write_all(data, path)


def clear_all(role=None, path=None):
    with _LOCK:
        data = _read_all(path)
        if role is None:
            data = {}
        else:
            data = {k: v for k, v in data.items() if v.get("role") != role}
        _write_all(data, path)
