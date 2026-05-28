from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from rule_based_coordinator import classify


ROOT = Path(__file__).resolve().parent
TESTS = ROOT / "coordinator_routing_tests.jsonl"

SYSTEM = """Return only compact JSON with keys:
intent, organ, organ_chain, tools_needed, confidence.
Valid organs: code-organ, reason-organ, data-organ, debug-organ, synthesis-organ, gate-organ, coordinator-organ.
Valid intents: route, code, reason, classify, retrieve, summarize, plan, debug, evaluate, handoff."""


def _extract_json(content: str) -> dict:
    candidates = []
    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.DOTALL)
    candidates.extend(fenced)
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(content[start : end + 1])
    candidates.append(content)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
    raise json.JSONDecodeError(str(last_error or "no JSON object found"), content, 0)


def call_model(base_url: str, api_key: str, model: str, query: str, timeout: int, max_tokens: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": query},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data["choices"][0]["message"].get("content") or ""
    return _extract_json(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="coordinator-minicpm5")
    parser.add_argument("--base-url", default="http://localhost:4000/v1")
    parser.add_argument("--api-key", default=os.getenv("LITELLM_MASTER_KEY", "sk-litellm-master-2026"))
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--max-tokens", type=int, default=768)
    args = parser.parse_args()

    failures = []
    for line in TESTS.read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        try:
            if args.model == "rule-based":
                got = classify(case["query"])
            else:
                got = call_model(args.base_url, args.api_key, args.model, case["query"], args.timeout, args.max_tokens)
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as exc:
            failures.append((case["id"], f"call/parse failed: {exc}"))
            continue

        if got.get("intent") != case["expected_intent"]:
            failures.append((case["id"], f"intent {got.get('intent')} != {case['expected_intent']}"))
        if got.get("organ") != case["expected_organ"]:
            failures.append((case["id"], f"organ {got.get('organ')} != {case['expected_organ']}"))
        if not isinstance(got.get("organ_chain"), list) or not got["organ_chain"]:
            failures.append((case["id"], "organ_chain missing/empty"))
        if not isinstance(got.get("tools_needed"), list):
            failures.append((case["id"], "tools_needed must be a list"))
        if not isinstance(got.get("confidence"), (int, float)):
            failures.append((case["id"], "confidence must be numeric"))

    if failures:
        print(json.dumps({"model": args.model, "passed": False, "failures": failures}, indent=2))
        return 1
    print(json.dumps({"model": args.model, "passed": True, "cases": 10}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
