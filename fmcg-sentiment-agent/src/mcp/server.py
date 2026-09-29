"""
server.py

MCP server that exposes the review tools over stdio. Agents and the test
client discover the tools and their schemas from it.

Run (normally started by a client, not by hand):
    python -m src.mcp.server
"""

import asyncio
import inspect
import json
import logging
import sys

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server

from src.config.logging_config import configure_logging
from src.mcp.registry import call_tool, list_specs, warm_up

logger = logging.getLogger(__name__)

server = Server("review-intelligence")


def call_tool_decorator():
    if "validate_input" in inspect.signature(server.call_tool).parameters:
        return server.call_tool(validate_input=False)
    return server.call_tool()


@server.list_tools()
async def handle_list_tools():
    return [
        types.Tool(name=spec["name"], description=spec["description"], inputSchema=spec["input_schema"])
        for spec in list_specs()
    ]


@call_tool_decorator()
async def handle_call_tool(name, arguments):
    result = await asyncio.to_thread(call_tool, name, arguments)
    return [types.TextContent(type="text", text=json.dumps(result, default=str))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    configure_logging(stream=sys.stderr)
    logger.info("Loading retrieval models, this takes up to a minute...")
    warm_up()
    logger.info("Ready.")
    asyncio.run(main())


