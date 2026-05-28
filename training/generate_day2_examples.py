from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "examples" / "ground_truth.jsonl"

PROFILES = {
    "code-organ": {"temperature": 0.1, "precision": 0.95, "reasoning_depth": 0.85, "creativity": 0.1},
    "reason-organ": {"temperature": 0.3, "precision": 0.80, "reasoning_depth": 0.95, "creativity": 0.2},
    "data-organ": {"temperature": 0.05, "precision": 0.98, "reasoning_depth": 0.75, "creativity": 0.0},
    "debug-organ": {"temperature": 0.1, "precision": 0.90, "reasoning_depth": 0.90, "creativity": 0.0},
    "synthesis-organ": {"temperature": 0.6, "precision": 0.70, "reasoning_depth": 0.80, "creativity": 0.7},
}

REAL_AST_CONTEXTS = [
    {
        "source": "memgraph:code-review-graph",
        "query": "MATCH (n:CodeNode) WHERE n.file_path = 'tests/test_tools.py' RETURN n LIMIT 4",
        "nodes": [
            {"label": "Module", "name": "tests/test_tools.py", "file_path": "tests/test_tools.py", "start_line": 1, "end_line": 1149},
            {"label": "Class", "name": "TestTools", "file_path": "tests/test_tools.py", "start_line": 21, "end_line": 151},
            {"label": "Method", "name": "setup_method", "file_path": "tests/test_tools.py", "start_line": 22, "end_line": 25},
            {"label": "Method", "name": "teardown_method", "file_path": "tests/test_tools.py", "start_line": 27, "end_line": 29},
        ],
        "edges": [
            {"type": "EDGE", "from": "tests/test_tools.py", "to": "TestTools"},
            {"type": "EDGE", "from": "TestTools", "to": "setup_method"},
            {"type": "EDGE", "from": "TestTools", "to": "teardown_method"},
        ],
    },
    {
        "source": "memgraph:code-review-graph",
        "query": "MATCH (n:CodeNode) WHERE n.file_path STARTS WITH 'code_review_graph/eval' RETURN n LIMIT 4",
        "nodes": [
            {"label": "Folder", "name": "code_review_graph", "file_path": "code_review_graph", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "eval", "file_path": "code_review_graph/eval", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "benchmarks", "file_path": "code_review_graph/eval/benchmarks", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "configs", "file_path": "code_review_graph/eval/configs", "start_line": 0, "end_line": 0},
        ],
        "edges": [
            {"type": "EDGE", "from": "code_review_graph", "to": "eval"},
            {"type": "EDGE", "from": "eval", "to": "benchmarks"},
            {"type": "EDGE", "from": "eval", "to": "configs"},
        ],
    },
    {
        "source": "memgraph:code-review-graph",
        "query": "MATCH (n:CodeNode) WHERE n.file_path STARTS WITH 'skills' RETURN n LIMIT 4",
        "nodes": [
            {"label": "Folder", "name": "skills", "file_path": "skills", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "debug-issue", "file_path": "skills/debug-issue", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "build-graph", "file_path": "skills/build-graph", "start_line": 0, "end_line": 0},
            {"label": "Folder", "name": "review-pr", "file_path": "skills/review-pr", "start_line": 0, "end_line": 0},
        ],
        "edges": [
            {"type": "EDGE", "from": "skills", "to": "debug-issue"},
            {"type": "EDGE", "from": "skills", "to": "build-graph"},
            {"type": "EDGE", "from": "skills", "to": "review-pr"},
        ],
    },
]

GRAPHITI_CONTEXTS = [
    {
        "source": "graphiti:temporal-memory",
        "query": "MATCH (e1:Entity)-[r:Relationship]->(e2:Entity) RETURN e1, r, e2",
        "edges": [
            {
                "from": "user",
                "to": "pytest",
                "relation": "PREFERS_TEST_FRAMEWORK",
                "valid_from": "2026-05-20T10:00:00Z",
                "valid_to": None,
                "invalid_at": None,
            },
            {
                "from": "user",
                "to": "unittest",
                "relation": "PREFERS_TEST_FRAMEWORK",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": "2026-05-20T10:00:00Z",
                "invalid_at": "2026-05-20T10:00:00Z",
            },
        ]
    }
]

CODE_TASKS = [
    ("clamp a numeric value inside inclusive bounds", "def clamp(value, lower, upper):\n    return max(lower, min(value, upper))"),
    ("dedupe a list while preserving order", "def dedupe(items):\n    seen = set()\n    out = []\n    for item in items:\n        if item not in seen:\n            seen.add(item)\n            out.append(item)\n    return out"),
    ("parse yes/no text into a boolean", "def parse_bool(text):\n    return str(text).strip().lower() in {'1', 'true', 'yes', 'y', 'on'}"),
    ("chunk a list into fixed-size groups", "def chunks(items, size):\n    return [items[i:i + size] for i in range(0, len(items), size)]"),
    ("return the top n numbers descending", "def top_n(values, n):\n    return sorted(values, reverse=True)[:n]"),
    ("normalize whitespace in a string", "def normalize_space(text):\n    return ' '.join(str(text).split())"),
    ("safe nested dictionary lookup", "def safe_get(data, path, default=None):\n    cur = data\n    for key in path:\n        if not isinstance(cur, dict) or key not in cur:\n            return default\n        cur = cur[key]\n    return cur"),
    ("build a slug from a title", "import re\n\ndef slugify(title):\n    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')"),
    ("merge counters without mutating inputs", "def merge_counts(a, b):\n    out = dict(a)\n    for key, value in b.items():\n        out[key] = out.get(key, 0) + value\n    return out"),
    ("format bytes into KiB text", "def kibibytes(num_bytes):\n    return f'{num_bytes / 1024:.1f} KiB'"),
]

REASON_TOPICS = [
    "choose local organ versus cloud fallback",
    "decide whether a task is code or plan",
    "explain why AST context reduces token use",
    "triage slow inference from memory pressure",
    "rank retrieval sources for a code question",
    "separate classifier confidence from correctness",
    "choose retry versus escalation after a gate failure",
    "explain why Gemini quota should not block routing",
    "reason about LoRA rank after ablation",
    "decide whether to use Coderunner for validation",
]

DATA_TASKS = [
    ("classify this request into the ten-intent schema", "classify", {"intent": "str", "confidence": "float"}),
    ("retrieve graph neighbors for a symbol", "retrieve", None),
    ("evaluate whether an organ output follows schema", "evaluate", {"valid": "bool", "reason": "str"}),
    ("classify an error as infra, model, data, or code", "classify", {"class": "str", "confidence": "float"}),
    ("retrieve Context7 docs for a library version", "retrieve", None),
    ("evaluate if an output should be handed off", "evaluate", {"handoff": "bool", "target": "str"}),
]

DEBUG_TASKS = [
    ("NameError for missing variable in generated code", "name 'total' is not defined", "def total_or_zero(values):\n    total = 0\n    for value in values:\n        total += value\n    return total"),
    ("TypeError when None is passed to len", "object of type 'NoneType' has no len()", "def safe_len(value):\n    return 0 if value is None else len(value)"),
    ("IndexError on empty result list", "list index out of range", "def first_or_none(items):\n    return items[0] if items else None"),
    ("JSON decode error on blank response", "Expecting value: line 1 column 1", "import json\n\ndef parse_json_or_empty(text):\n    return {} if not text.strip() else json.loads(text)"),
    ("division by zero in metric code", "division by zero", "def ratio(part, whole):\n    return 0 if whole == 0 else part / whole"),
]

SYNTHESIS_TASKS = [
    ("summarize code, reason, and debug organ findings", "summarize"),
    ("handoff a failed gate result to Activepieces", "handoff"),
    ("route a mixed request across code and data organs", "route"),
    ("summarize Langfuse trace findings for the user", "summarize"),
    ("handoff quota restoration to a human operator", "handoff"),
    ("route a retrieval-heavy bug report", "route"),
]


def ast_context(index: int) -> dict[str, Any] | None:
    if index >= 6:
        return None
    return REAL_AST_CONTEXTS[index % len(REAL_AST_CONTEXTS)]


def graphiti_context(index: int) -> dict[str, Any] | None:
    # 10% injection split (3 out of 30 examples per organ)
    if index % 10 == 0:
        return GRAPHITI_CONTEXTS[0]
    return None


def base_example(
    organ: str,
    index: int,
    intent: str,
    query: str,
    tools: list[str],
    steps: list[str],
    response: str,
    *,
    exec_ready: bool = False,
    pytest_assertions: str | None = None,
    code: str | None = None,
    error: str | None = None,
    output_format: str = "text",
    expected_schema: dict[str, str] | None = None,
    notes: str = "Day 2 ground truth example.",
) -> dict[str, Any]:
    rationalization = f"Routing {query} to {organ} because it targets {intent}."
    return {
        "id": f"{organ}-{index + 1:02d}",
        "query": query,
        "target_organ": organ,
        "coordinator": {
            "rationalization": rationalization,
            "intent": intent,
            "organ": organ,
            "organ_chain": [organ],
            "docoreai_profile": PROFILES[organ],
            "confidence": 0.86,
            "tools_needed": tools,
        },
        "organ_output": {
            "intent": intent,
            "exec_ready": exec_ready,
            "pytest_assertions": pytest_assertions,
            "code_executable": code,
            "tools_needed": tools,
            "steps": steps,
            "error": error,
            "output_format": output_format,
            "response": response,
            "expected_schema": expected_schema,
        },
        "ast_context": ast_context(index),
        "graphiti_context": graphiti_context(index),
        "notes": notes,
    }


def code_examples() -> list[dict[str, Any]]:
    examples = []
    for index in range(30):
        task, code = CODE_TASKS[index % len(CODE_TASKS)]
        func_name = code.split('(')[0].split('def ')[1]
        pytest_mock = f"def test_{func_name}():\n    assert {func_name} != None"
        examples.append(base_example(
            "code-organ",
            index,
            "code",
            f"Write runnable Python to {task}.",
            ["python-code-runner", "query_graph", "find_symbol"],
            [
                f"Identify the function contract for {task}.",
                f"Use the contract for {task} to keep edge cases explicit.",
                f"Return compact runnable Python for {task}.",
            ],
            f"Implemented {task} as a small runnable helper.",
            exec_ready=True,
            pytest_assertions=pytest_mock,
            code=code,
            output_format="code",
            notes="Code organ primary-intent example.",
        ))
    return examples


def reason_examples() -> list[dict[str, Any]]:
    examples = []
    for index in range(30):
        topic = REASON_TOPICS[index % len(REASON_TOPICS)]
        intent = "plan" if index % 5 == 4 else "reason"
        verb = "Plan" if intent == "plan" else "Reason through"
        examples.append(base_example(
            "reason-organ",
            index,
            intent,
            f"{verb} how to {topic}.",
            ["query_graph", "search_graph", "query-docs"],
            [
                f"Start from the goal: {topic}.",
                f"Use {topic} to identify the blocking constraint.",
                f"Resolve the constraint in {topic} before choosing the next action.",
            ],
            f"{topic}: constraint first, evidence second, action third.",
            output_format="text",
            notes="Reason organ chain-step example.",
        ))
    return examples


def data_examples() -> list[dict[str, Any]]:
    examples = []
    for index in range(30):
        task, intent, schema = DATA_TASKS[index % len(DATA_TASKS)]
        tools = ["query_graph", "search_code"] if intent == "retrieve" else ["query_graph"]
        if intent == "retrieve":
            response = json.dumps({"source": "memgraph", "result": "relevant nodes returned"})
            output_format = "json"
            expected = {"source": "str", "result": "str"}
        elif intent == "classify":
            response = json.dumps({"class": "code", "intent": "code", "confidence": 0.91})
            output_format = "json"
            expected = schema
        else:
            response = json.dumps({"valid": True, "reason": "required fields are present", "handoff": False, "target": ""})
            output_format = "json"
            expected = schema
        examples.append(base_example(
            "data-organ",
            index,
            intent,
            f"{task}.",
            tools,
            [
                f"Normalize the data request: {task}.",
                f"Apply schema rules to {task}.",
                f"Return the smallest valid JSON result for {task}.",
            ],
            response,
            output_format=output_format,
            expected_schema=expected,
            notes="Data organ schema or retrieval example.",
        ))
    return examples


def debug_examples() -> list[dict[str, Any]]:
    examples = []
    for index in range(30):
        task, error, code = DEBUG_TASKS[index % len(DEBUG_TASKS)]
        examples.append(base_example(
            "debug-organ",
            index,
            "debug",
            f"Fix this failure: {task}. Error: {error}.",
            ["python-code-runner", "query_graph", "find_referencing_symbols"],
            [
                f"Reproduce the failure from error: {error}.",
                f"Trace {error} to the smallest invalid assumption.",
                f"Patch the assumption and return executable code for {task}.",
            ],
            f"Fixed {task} by guarding the failing edge case.",
            exec_ready=True,
            code=code,
            error=error,
            output_format="code",
            notes="Debug organ executable-fix example.",
        ))
    return examples


def synthesis_examples() -> list[dict[str, Any]]:
    examples = []
    for index in range(30):
        task, intent = SYNTHESIS_TASKS[index % len(SYNTHESIS_TASKS)]
        tools = ["query_graph"] if intent == "route" else []
        response = {
            "summarize": f"{task}: merged findings into a short user-facing answer.",
            "handoff": f"{task}: send concise payload to Activepieces with owner and reason.",
            "route": f"{task}: code-organ then data-organ, gate-organ validates both.",
        }[intent]
        examples.append(base_example(
            "synthesis-organ",
            index,
            intent,
            f"{task}.",
            tools,
            [
                f"Collect upstream outputs for {task}.",
                f"Remove conflicts in {task} before final wording.",
                f"Return a dense final result for {task}.",
            ],
            response,
            output_format="text",
            notes="Synthesis organ dense-output example.",
        ))
    return examples


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    examples = code_examples() + reason_examples() + data_examples() + debug_examples() + synthesis_examples()
    with OUT.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, sort_keys=True) + "\n")
    print(f"wrote {len(examples)} examples to {OUT}")


if __name__ == "__main__":
    main()

