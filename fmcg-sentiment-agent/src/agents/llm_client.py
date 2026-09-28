"""
llm_client.py
"""


import argparse
import json
import os
import time
from pathlib import Path


from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")


PROVIDERS = {
    "groq": {"base_url": "https://api.groq.com/openai/v1", "key_env": "GROQ_API_KEY"},
    "openrouter": {"base_url": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "key_env": "GOOGLE_API_KEY"},
    "nvidia": {"base_url": "https://integrate.api.nvidia.com/v1", "key_env": "NVIDIA_API_KEY"},
    "mistral": {"base_url": "https://api.mistral.ai/v1", "key_env": "MISTRAL_API_KEY"},
}


TOOL_TEST_SYSTEM = (
    "You answer questions about customer reviews. Use the provided tools to get data. "
    "Do not answer from memory."
)


TOOL_TESTS = [
    {"question": "How did sentiment on packaging change over the last 3 months?",
     "tool": "sentiment_trend", "args": {"aspect": "packaging"}},
    {"question": "Show me the high-severity flagged reviews from the last 7 days.",
     "tool": "flagged_reviews", "args": {"severity_level": "high", "last_n_days": 7}},
]




def resolve(model_spec):
    provider, _, model = model_spec.partition(":")
    if provider not in PROVIDERS or not model:
        raise ValueError(f"Use provider:model_id with a provider from {list(PROVIDERS)}. Got '{model_spec}'.")
    config = PROVIDERS[provider]
    api_key = os.environ.get(config["key_env"])
    if not api_key:
        raise ValueError(f"{config['key_env']} not found in .env")
    return {"provider": provider, "model": model, "base_url": config["base_url"], "api_key": api_key}




def clean_schema(schema):
    if isinstance(schema, dict):
        return {k: clean_schema(v) for k, v in schema.items() if k != "additionalProperties"}
    if isinstance(schema, list):
        return [clean_schema(v) for v in schema]
    return schema




def to_openai_tools(specs, provider):
    tools = []
    for spec in specs:
        schema = clean_schema(spec["input_schema"]) if provider == "gemini" else spec["input_schema"]
        tools.append({
            "type": "function",
            "function": {"name": spec["name"], "description": spec["description"], "parameters": schema},
        })
    return tools




def parse_arguments(raw):
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}




def chat(model_spec, messages, tool_specs=None, temperature=0.2, max_tokens=1500):
    from openai import OpenAI


    config = resolve(model_spec)
    client = OpenAI(base_url=config["base_url"], api_key=config["api_key"], timeout=90, max_retries=3)


    kwargs = {"model": config["model"], "messages": messages, "max_tokens": max_tokens}
    if config["provider"] != "gemini":
        kwargs["temperature"] = temperature
    if tool_specs:
        kwargs["tools"] = to_openai_tools(tool_specs, config["provider"])
        kwargs["tool_choice"] = "auto"


    started = time.time()
    response = client.chat.completions.create(**kwargs)
    latency = round(time.time() - started, 2)


    message = response.choices[0].message
    calls = [
        {"id": c.id, "name": c.function.name, "arguments": parse_arguments(c.function.arguments)}
        for c in (message.tool_calls or [])
    ]
    usage = response.usage
    return {
        "model": model_spec,
        "content": message.content or "",
        "tool_calls": calls,
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        "latency_sec": latency,
    }




def run_tool_test(model_spec):
    from src.mcp.registry import list_specs


    specs = list_specs()
    passed = 0
    for test in TOOL_TESTS:
        messages = [
            {"role": "system", "content": TOOL_TEST_SYSTEM},
            {"role": "user", "content": test["question"]},
        ]
        result = chat(model_spec, messages, specs)
        calls = result["tool_calls"]
        first = calls[0] if calls else None
        name_ok = bool(first) and first["name"] == test["tool"]
        args_ok = name_ok and all(first["arguments"].get(k) == v for k, v in test["args"].items())
        passed += int(name_ok and args_ok)
        print(f"Question: {test['question']}")
        print(f"  called: {[(c['name'], c['arguments']) for c in calls] or 'no tool call'}")
        print(f"  expected: {test['tool']} {test['args']} -> {'PASS' if name_ok and args_ok else 'FAIL'}")
        print(f"  {result['latency_sec']}s, {result['prompt_tokens']} prompt tokens, {result['completion_tokens']} completion tokens")
    print(f"Passed {passed} of {len(TOOL_TESTS)}")




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt", default="Reply with the single word OK.")
    ap.add_argument("--tool-test", action="store_true")
    args = ap.parse_args()


    print(f"Model: {args.model}")
    if args.tool_test:
        run_tool_test(args.model)
        return


    result = chat(args.model, [{"role": "user", "content": args.prompt}])
    print(f"Reply: {result['content'].strip()}")
    print(f"{result['latency_sec']}s, {result['prompt_tokens']} prompt tokens, {result['completion_tokens']} completion tokens")




if __name__ == "__main__":
    main()



