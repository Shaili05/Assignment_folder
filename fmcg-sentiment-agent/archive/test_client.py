"""
test_client.py

Starts the MCP server as a subprocess, lists its tools and calls each one.
Also sends an invalid aspect and an unknown tool to confirm errors come back
as data instead of crashing the server.

The server loads its models at startup, so the first connection can take up
to a minute. Every step has a timeout so a stuck server is reported.

Run:
    python src/mcp_server/test_client.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).resolve().parent / "server.py"
STARTUP_TIMEOUT = 300
CALL_TIMEOUT = 120

CALLS = [
    ("sentiment_trend", {"aspect": "packaging", "granularity": "month", "periods": 3}),
    ("flagged_reviews", {"severity_level": "high", "last_n_days": 365, "limit": 2}),
    ("generate_summary_report", {"window_days": 30}),
    ("search_reviews", {"question": "packaging complaints", "top_k": 3, "aspect": "packaging"}),
    ("sentiment_trend", {"aspect": "colour"}),
    ("delete_everything", {}),
]


def summarize(name, data):
    if "error" in data:
        return f"error: {data['error']}"
    if name == "sentiment_trend":
        rows = [f"{r['period']}: n={r['n_reviews']}, net {r['net_sentiment']}" for r in data["series"]]
        return " | ".join(rows)
    if name == "flagged_reviews":
        ids = [r["review_id"] for r in data["reviews"]]
        return f"total_matches={data['total_matches']}, returned ids={ids}"
    if name == "generate_summary_report":
        return data["markdown"].splitlines()[0] + " / " + data["markdown"].splitlines()[2]
    if name == "search_reviews":
        return ", ".join(f"R{r['review_id']} (sim {r['similarity']})" for r in data["reviews"])
    return str(data)[:200]


def read_result(result):
    # The SDK rejects schema violations itself and returns plain error text.
    text = result.content[0].text if result.content else ""
    if getattr(result, "isError", False):
        return {"error": text}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": text}


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER_PATH)], env=dict(os.environ))
    print("Starting server, models are loading...", flush=True)
    started = time.time()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), STARTUP_TIMEOUT)
            print(f"Server ready after {time.time() - started:.0f}s", flush=True)
            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}", flush=True)
            for name, arguments in CALLS:
                started = time.time()
                try:
                    result = await asyncio.wait_for(session.call_tool(name, arguments), CALL_TIMEOUT)
                except asyncio.TimeoutError:
                    print(f"{name} {arguments}\n  timed out after {CALL_TIMEOUT}s", flush=True)
                    continue
                data = read_result(result)
                print(f"{name} {arguments}", flush=True)
                print(f"  {summarize(name, data)} ({time.time() - started:.1f}s)", flush=True)


if __name__ == "__main__":
    asyncio.run(main())


