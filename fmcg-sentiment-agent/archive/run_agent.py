"""
run_agent.py

Command line entry point for the review agent. Several --question flags are
sent one after another in the same session, which tests conversation memory.

Run:
    python src/agent/run_agent.py --framework langgraph --model groq:openai/gpt-oss-120b --question "How did sentiment on packaging change over the last 3 months?"
    python src/agent/run_agent.py --question "Show me the high-severity flagged reviews from the last 30 days." --question "Which product had the worst one?"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.audit import new_session_id
from agent.roles import DEFAULT_ROLE, ROLES
from agent.runtime import AgentRuntime


def print_record(record):
    print(f"Q: {record['question']}")
    print(f"Status: {record['status']}")
    print(f"Answer: {record['answer']}")
    for call in record["tool_calls"]:
        print(f"  tool {call['name']} {json.dumps(call['arguments'])} -> {len(call.get('output_text') or '')} chars")
    checks = record.get("checks") or {}
    if checks:
        print(f"  checks: invalid citations {checks['invalid_citations']}, unsupported quotes "
              f"{checks['unsupported_quotes']}, unsupported numbers {checks['unsupported_numbers']}, "
              f"injection detected {checks['injection_detected']}")
    print(f"  {record['latency_sec']}s, {record['prompt_tokens']} prompt tokens, "
          f"{record['completion_tokens']} completion tokens, cost {record.get('cost_usd')}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--framework", default="langgraph", choices=["langgraph", "autogen"])
    ap.add_argument("--model", default="groq:openai/gpt-oss-120b")
    ap.add_argument("--role", default=DEFAULT_ROLE, choices=list(ROLES))
    ap.add_argument("--question", action="append", required=True)
    args = ap.parse_args()

    print(f"Starting {args.framework} agent with {args.model}, the tool server needs up to a minute...", flush=True)
    runtime = AgentRuntime(args.framework, args.model)
    session_id = new_session_id()
    try:
        runtime.wait_until_ready()
        print("Ready.", flush=True)
        for question in args.question:
            print_record(runtime.ask(question, args.role, session_id))
    finally:
        runtime.close()


if __name__ == "__main__":
    main()


