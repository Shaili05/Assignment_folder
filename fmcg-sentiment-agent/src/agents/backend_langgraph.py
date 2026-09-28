"""
backend_langgraph.py

Agent backend built with LangChain's create_agent (LangGraph runtime).
Tools come from the MCP server through langchain-mcp-adapters, over one
persistent session. Conversation memory is a LangGraph checkpointer keyed by
session id.
"""

import contextlib
import os
import sys
from pathlib import Path

from src.agents.llm_client import resolve
from src.agents.prompts import build_system_prompt
from src.agents.roles import allowed_tools

REPO_ROOT = Path(__file__).resolve().parents[2]
RECURSION_LIMIT = 15


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


class LangGraphBackend:
    name = "langgraph"

    def __init__(self, model_spec):
        self.model_spec = model_spec
        self.stack = None
        self.tools = []
        self.llm = None
        self.checkpointer = None
        self.agents = {}

    async def open(self):
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain_mcp_adapters.tools import load_mcp_tools
        from langchain_openai import ChatOpenAI
        from langgraph.checkpoint.memory import InMemorySaver

        config = resolve(self.model_spec)
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

    async def close(self):
        if self.stack is not None:
            await self.stack.aclose()

    def get_agent(self, role):
        if role not in self.agents:
            from langchain.agents import create_agent

            permitted = set(allowed_tools(role))
            tools = [t for t in self.tools if t.name in permitted]
            self.agents[role] = create_agent(
                self.llm, tools, system_prompt=build_system_prompt(role), checkpointer=self.checkpointer,
            )
        return self.agents[role]

    async def ask(self, question, role, session_id):
        agent = self.get_agent(role)
        config = {"configurable": {"thread_id": f"{session_id}:{role}"}, "recursion_limit": RECURSION_LIMIT}
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


