import asyncio
import concurrent.futures
import contextlib
import logging
import os
import sys
import threading
import time

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from src.agents.roles import allowed_tools, get_role
from src.config.constants import (
    AGENT_LLM_MAX_RETRIES, AGENT_LLM_TIMEOUT, LLM_TEMPERATURE, MAX_TURNS_PER_THREAD, ROLE_FOCUS,
    RATE_LIMIT_STATUS_CODE, RECURSION_LIMIT, REQUEST_TIMEOUT, SHUTDOWN_TIMEOUT, STARTUP_TIMEOUT, TOKEN_LIMIT_STATUS_CODE,
    STAGE_CHECKS_PASSED, STAGE_CHECKS_STOPPED, STAGE_COMPLETED, STAGE_FAILED, STAGE_GROUNDING,
    STAGE_QUESTION_RECEIVED,
    EMPTY_ANSWER_MESSAGE,
)


from src.config.prompts import AGENT_PROMPT
from src.config.settings import REPO_ROOT, resolve_model
from src.exceptions.exceptions import (
    AgentExecutionError, AppError, AssistantTimeoutError, AssistantUnavailableError, RateLimitError,
)
from src.guardrails.grounding import GROUNDING_PROBLEM_KEYS, check_grounding, collect_reviews
from src.guardrails.input_checks import check_question, check_role_access
from src.utils.audit_logger import log_interaction
from src.utils.progress_log import StageCallback, log_stage

logger = logging.getLogger(__name__)


def build_system_prompt(role):
    info = get_role(role)
    tools = ", ".join(info["tools"])
    focus = ROLE_FOCUS[role]
    return f"{AGENT_PROMPT}\n\nThe user's role: {info['label']}. {focus} You may only use these tools: {tools}."


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


def precheck(question, has_history, role=None):
    check = check_question(question)
    if check["status"] == "clarify" and has_history:
        check = {"status": "ok", "message": ""}
    if check["status"] == "ok" and role:
        return check_role_access(question, role) or check
    return check


def audit_copy(record):
    entry = {k: v for k, v in record.items() if k != "tool_calls"}
    entry["tool_calls"] = [
        {"name": c["name"], "arguments": c["arguments"], "output_chars": len(c.get("output_text") or "")}
        for c in record.get("tool_calls", [])
    ]
    return entry


def to_app_error(exc):
    if isinstance(exc, AppError):
        return exc
    if getattr(exc, "status_code", None) in (RATE_LIMIT_STATUS_CODE, TOKEN_LIMIT_STATUS_CODE):
        return RateLimitError()
    return AgentExecutionError()


def error_detail(exc):
    cause = exc.__cause__ or exc
    return f"{cause.__class__.__name__}: {cause}"


def latest_turn(messages):
    last_human = max(i for i, m in enumerate(messages) if m.type == "human")
    return messages[last_human + 1:]


def tool_results_by_call_id(turn):
    results = {}
    for message in turn:
        if message.type == "tool":
            results[message.tool_call_id] = (text_of(message.content), getattr(message, "status", "success"))
    return results


def summarize_turn(turn):
    results = tool_results_by_call_id(turn)
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
    return tool_calls, prompt_tokens, completion_tokens


def final_answer(turn):
    final_message = turn[-1] if turn else None
    if final_message is None or final_message.type != "ai":
        return EMPTY_ANSWER_MESSAGE
    return text_of(final_message.content).strip() or EMPTY_ANSWER_MESSAGE


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
        config = resolve_model(self.model_spec)
        options = {
            "model": config["model"], "base_url": config["base_url"], "api_key": config["api_key"],
            "timeout": AGENT_LLM_TIMEOUT, "max_retries": AGENT_LLM_MAX_RETRIES,
        }
        if config["provider"] != "gemini":
            options["temperature"] = LLM_TEMPERATURE
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

    def _run_config(self, session_id, role):
        return {
            "configurable": {"thread_id": self._thread_id_for(session_id, role)},
            "recursion_limit": RECURSION_LIMIT,
            "callbacks": [StageCallback(session_id, role)],
        }

    async def _invoke(self, question, role, session_id):
        agent = self._get_agent(role)
        config = self._run_config(session_id, role)
        try:
            output = await agent.ainvoke({"messages": [{"role": "user", "content": question}]}, config=config)
        except Exception as exc:
            raise to_app_error(exc) from exc

        turn = latest_turn(output["messages"])
        tool_calls, prompt_tokens, completion_tokens = summarize_turn(turn)
        return {
            "answer": final_answer(turn), "tool_calls": tool_calls,
            "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
        }

    def _log_without_answer(self, base, status, answer, latency_sec=0.0, error_detail_text=None):
        record = {
            **base, "status": status, "answer": answer, "tool_calls": [],
            "prompt_tokens": 0, "completion_tokens": 0, "latency_sec": latency_sec, "checks": {},
        }
        if error_detail_text:
            record["error_detail"] = error_detail_text
        record["interaction_id"] = log_interaction(audit_copy(record), self.audit_path)["interaction_id"]
        return record

    async def _answer_turn(self, question, role, session_id):
        base = {
            "session_id": session_id, "role": role, "framework": self.name,
            "model": self.model_spec, "question": question,
        }
        log_stage(session_id, role, STAGE_QUESTION_RECEIVED, question[:80])
        check = precheck(question, self.turn_counts.get(session_id, 0) > 0, role)
        if check["status"] != "ok":
            log_stage(session_id, role, STAGE_CHECKS_STOPPED, check["status"])
            return self._log_without_answer(base, check["status"], check["message"])

        log_stage(session_id, role, STAGE_CHECKS_PASSED)
        started = time.time()
        try:
            raw = await self._invoke(question, role, session_id)
        except AppError as exc:
            logger.exception("The agent failed on a question (session %s, role %s)", session_id, role)
            log_stage(session_id, role, STAGE_FAILED, error_detail(exc))
            return self._log_without_answer(
                base, "error", exc.message, round(time.time() - started, 2), error_detail(exc),
            )

        self.turn_counts[session_id] = self.turn_counts.get(session_id, 0) + 1
        previous = self.session_reviews.get(session_id, {})
        checks = check_grounding(raw["answer"], question, raw["tool_calls"], previous)
        self.session_reviews[session_id] = {**previous, **collect_reviews(raw["tool_calls"])}
        problems = [name for name in GROUNDING_PROBLEM_KEYS if checks[name]]
        log_stage(session_id, role, STAGE_GROUNDING, ", ".join(problems) or "ok")
        record = {
            **base, "status": "answered", "answer": raw["answer"], "tool_calls": raw["tool_calls"],
            "prompt_tokens": raw["prompt_tokens"], "completion_tokens": raw["completion_tokens"],
            "latency_sec": round(time.time() - started, 2), "checks": checks,
        }
        entry = log_interaction(audit_copy(record), self.audit_path)
        record["interaction_id"] = entry["interaction_id"]
        record["cost_usd"] = entry.get("cost_usd")
        log_stage(session_id, role, STAGE_COMPLETED, f"interaction {entry['interaction_id']}, {record['latency_sec']} s")
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
        self.thread.join(timeout=SHUTDOWN_TIMEOUT)
        logger.info("The assistant was shut down")


