"""
review_agent.py

The one review-intelligence agent.

  - LangGraph agent whose tools come from the MCP server (one persistent session)
  - runs on its own event loop in a background thread, so plain synchronous
    code (FastAPI services, the evaluation script) can call ask()
  - one turn = input checks -> agent -> grounding checks -> audit log

MCP connections must be opened and closed from the same task, so the session
and the agents live inside one long-running task and requests reach it
through a queue. A session moves to a fresh context window after
MAX_TURNS_PER_THREAD questions to keep prompt size (latency, tokens) bounded.

Errors inside a turn are logged in full, but the user only sees a short,
safe message. The technical detail is kept in the audit record (error_detail).
"""

import asyncio
import concurrent.futures
import contextlib
import logging
import os
import sys
import threading
import time

from src.agents.roles import allowed_tools, get_role
from src.config.constants import MAX_TURNS_PER_THREAD
from src.config.prompts import AGENT_PROMPT
from src.config.settings import REPO_ROOT, resolve_model
from src.exceptions.exceptions import (
    AppError, AssistantTimeoutError, AssistantUnavailableError, RateLimitError,
)
from src.guardrails.grounding import check_grounding, collect_reviews
from src.guardrails.input_checks import check_question
from src.utils.audit_logger import log_interaction

logger = logging.getLogger(__name__)

STARTUP_TIMEOUT = 400
REQUEST_TIMEOUT = 480
RECURSION_LIMIT = 15
GENERIC_ERROR_MESSAGE = "The assistant hit an error. Please try again."


def build_system_prompt(role):
    info = get_role(role)
    tools = ", ".join(info["tools"])
    return f"{AGENT_PROMPT}\n\nThe user's role: {info['label']}. You may only use these tools: {tools}."


def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict):
            parts.append(block.get("text", ""))
        else:
            parts.append(str(block))
    return "".join(parts)


def precheck(question, has_history):
    check = check_question(question)
    if check["status"] == "clarify" and has_history:
        return {"status": "ok", "message": ""}
    return check


def audit_copy(record):
    entry = {k: v for k, v in record.items() if k != "tool_calls"}
    entry["tool_calls"] = [
        {"name": c["name"], "arguments": c["arguments"], "output_chars": len(c.get("output_text") or "")}
        for c in record.get("tool_calls", [])
    ]
    return entry


def friendly_error(exc):
    if getattr(exc, "status_code", None) == 429:
        return RateLimitError.default_message
    if isinstance(exc, AppError):
        return exc.message
    return GENERIC_ERROR_MESSAGE


def error_detail(exc):
    return f"{exc.__class__.__name__}: {exc}"


class ReviewAgent:
    name = "langgraph"

    def __init__(self, model_spec, audit_path=None):
        self.model_spec = model_spec
        self.audit_path = audit_path
        self.stack = None
        self.tools = []
        self.llm = None
        self.checkpointer = None
        self.agents = {}
        self.turns = {}           
        self.generation = {}      
        self.turn_counts = {}     
        self.session_reviews = {} 
        self.ready = threading.Event()
        self.startup_error = None
        self.queue = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    @staticmethod
    def _quiet_handler(loop, context):
        if "overlapped future" in str(context.get("message", "")):
            return
        loop.default_exception_handler(context)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.set_exception_handler(self._quiet_handler)
        task = self.loop.create_task(self._serve())
        task.add_done_callback(lambda _: self.loop.stop())
        self.loop.run_forever()

    async def _serve(self):
        self.queue = asyncio.Queue()
        try:
            await self._open()
        except Exception as exc:
            logger.exception("The assistant failed to start")
            self.startup_error = exc
            self.ready.set()
            await self._close()
            return
        logger.info("The assistant is ready (%s, %d tools)", self.model_spec, len(self.tools))
        self.ready.set()

        try:
            while True:
                item = await self.queue.get()
                if item is None:
                    break
                kwargs, future = item
                try:
                    result = await self._answer_turn(kwargs["question"], kwargs["role"], kwargs["session_id"])
                    future.set_result(result)
                except Exception as exc:
                    logger.exception("A turn failed outside the agent call")
                    future.set_exception(exc)
        finally:
            await self._close()

    async def _open(self):
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain_mcp_adapters.tools import load_mcp_tools
        from langchain_openai import ChatOpenAI
        from langgraph.checkpoint.memory import InMemorySaver

        config = resolve_model(self.model_spec)
        options = {"model": config["model"], "base_url": config["base_url"],
                   "api_key": config["api_key"], "timeout": 90, "max_retries": 3}
        if config["provider"] != "gemini":
            options["temperature"] = 0.2
        self.llm = ChatOpenAI(**options)
        self.checkpointer = InMemorySaver()

        client = MultiServerMCPClient({
            "reviews": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "src.mcp.server"],
                "cwd": str(REPO_ROOT),
                "env": dict(os.environ),
            }
        })
        self.stack = contextlib.AsyncExitStack()
        session = await self.stack.enter_async_context(client.session("reviews"))
        self.tools = await load_mcp_tools(session)
        for tool in self.tools:
            tool.handle_tool_error = True

    async def _close(self):
        if self.stack is not None:
            await self.stack.aclose()
            self.stack = None

    def _get_agent(self, role):
        if role not in self.agents:
            from langchain.agents import create_agent

            permitted = set(allowed_tools(role))
            tools = [t for t in self.tools if t.name in permitted]
            self.agents[role] = create_agent(
                self.llm, tools, system_prompt=build_system_prompt(role), checkpointer=self.checkpointer,
            )
        return self.agents[role]

    def _thread_id_for(self, session_id, role):
        key = f"{session_id}:{role}"
        if self.turns.get(key, 0) >= MAX_TURNS_PER_THREAD:
            self.generation[key] = self.generation.get(key, 0) + 1
            self.turns[key] = 0
            logger.info("Session %s moved to a fresh context window", session_id)
        self.turns[key] = self.turns.get(key, 0) + 1
        return f"{key}:{self.generation.get(key, 0)}"

    async def _invoke(self, question, role, session_id):
        agent = self._get_agent(role)
        config = {
            "configurable": {"thread_id": self._thread_id_for(session_id, role)},
            "recursion_limit": RECURSION_LIMIT,
        }
        output = await agent.ainvoke({"messages": [{"role": "user", "content": question}]}, config=config)

        messages = output["messages"]
        last_human = max(i for i, m in enumerate(messages) if m.type == "human")
        turn = messages[last_human + 1:]

        results = {}
        for message in turn:
            if message.type == "tool":
                results[message.tool_call_id] = (text_of(message.content), getattr(message, "status", "success"))

        tool_calls, prompt_tokens, completion_tokens = [], 0, 0
        for message in turn:
            if message.type != "ai":
                continue
            usage = getattr(message, "usage_metadata", None) or {}
            prompt_tokens += usage.get("input_tokens", 0)
            completion_tokens += usage.get("output_tokens", 0)
            for call in getattr(message, "tool_calls", None) or []:
                output_text, status = results.get(call["id"], ("", "missing"))
                tool_calls.append({
                    "name": call["name"], "arguments": call["args"],
                    "output_text": output_text, "ok": status != "error",
                })

        final = turn[-1] if turn else None
        answer = text_of(final.content).strip() if final is not None and final.type == "ai" else ""
        if not answer:
            answer = "I could not produce an answer. Please rephrase the question."
        return {"answer": answer, "tool_calls": tool_calls,
                "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}

    async def _answer_turn(self, question, role, session_id):
        base = {
            "session_id": session_id, "role": role, "framework": self.name,
            "model": self.model_spec, "question": question,
        }
        check = precheck(question, self.turn_counts.get(session_id, 0) > 0)
        if check["status"] != "ok":
            record = {**base, "status": check["status"], "answer": check["message"], "tool_calls": [],
                      "prompt_tokens": 0, "completion_tokens": 0, "latency_sec": 0.0, "checks": {}}
            record["interaction_id"] = log_interaction(audit_copy(record), self.audit_path)["interaction_id"]
            return record

        started = time.time()
        try:
            raw = await self._invoke(question, role, session_id)
        except Exception as exc:
            logger.exception("The agent failed on a question (session %s, role %s)", session_id, role)
            record = {**base, "status": "error", "answer": friendly_error(exc),
                      "error_detail": error_detail(exc), "tool_calls": [],
                      "prompt_tokens": 0, "completion_tokens": 0,
                      "latency_sec": round(time.time() - started, 2), "checks": {}}
            record["interaction_id"] = log_interaction(audit_copy(record), self.audit_path)["interaction_id"]
            return record

        self.turn_counts[session_id] = self.turn_counts.get(session_id, 0) + 1
        previous = self.session_reviews.get(session_id, {})
        checks = check_grounding(raw["answer"], question, raw["tool_calls"], previous)
        self.session_reviews[session_id] = {**previous, **collect_reviews(raw["tool_calls"])}
        record = {
            **base, "status": "answered", "answer": raw["answer"], "tool_calls": raw["tool_calls"],
            "prompt_tokens": raw["prompt_tokens"], "completion_tokens": raw["completion_tokens"],
            "latency_sec": round(time.time() - started, 2), "checks": checks,
        }
        entry = log_interaction(audit_copy(record), self.audit_path)
        record["interaction_id"] = entry["interaction_id"]
        record["cost_usd"] = entry.get("cost_usd")
        return record

    def wait_until_ready(self):
        if not self.ready.wait(STARTUP_TIMEOUT):
            raise AssistantUnavailableError("The assistant did not start in time.")
        if self.startup_error:
            if isinstance(self.startup_error, AppError):
                raise AssistantUnavailableError(f"The assistant failed to start: {self.startup_error.message}")
            raise AssistantUnavailableError("The assistant failed to start. See the server log for details.")

    def ask(self, question, role, session_id):
        get_role(role)
        self.wait_until_ready()
        future = concurrent.futures.Future()
        payload = ({"question": question, "role": role, "session_id": session_id}, future)
        self.loop.call_soon_threadsafe(self.queue.put_nowait, payload)
        try:
            return future.result(timeout=REQUEST_TIMEOUT)
        except concurrent.futures.TimeoutError as exc:
            logger.error("The assistant did not answer within %s seconds", REQUEST_TIMEOUT)
            raise AssistantTimeoutError() from exc

    def close(self):
        if self.queue is not None and self.ready.is_set() and not self.startup_error:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, None)
        self.thread.join(timeout=30)
        logger.info("The assistant was shut down")


