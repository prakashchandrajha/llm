from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable

from schema import OrganOutput, TrainingExample


REWARD_WEIGHTS = {
    "code-organ": {
        "code_executable_pass": 0.45,
        "required_fields": 0.20,
        "intent_valid": 0.15,
        "exec_consistency": 0.10,
        "token_economy": 0.10,
    },
    "reason-organ": {
        "chain_step_validity": 0.35,
        "required_fields": 0.20,
        "intent_valid": 0.20,
        "exec_consistency": 0.15,
        "token_economy": 0.10,
    },
    "debug-organ": {
        "code_executable_pass": 0.35,
        "required_fields": 0.20,
        "intent_valid": 0.20,
        "exec_consistency": 0.15,
        "token_economy": 0.10,
    },
    "data-organ": {
        "schema_match": 0.35,
        "required_fields": 0.25,
        "intent_valid": 0.20,
        "exec_consistency": 0.10,
        "token_economy": 0.10,
    },
    "synthesis-organ": {
        "coherence_score": 0.35,
        "required_fields": 0.20,
        "intent_valid": 0.20,
        "exec_consistency": 0.15,
        "token_economy": 0.10,
    },
}

INTENT_BY_ORGAN = {
    "code-organ": {"code"},
    "reason-organ": {"reason", "plan"},
    "data-organ": {"classify", "retrieve", "evaluate"},
    "debug-organ": {"debug", "code"},
    "synthesis-organ": {"summarize", "handoff", "route"},
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _token_count(parts: Iterable[str]) -> int:
    return sum(len(_tokens(part)) for part in parts)


def code_executable_pass(output: OrganOutput) -> float:
    if not output.code_executable:
        return 0.0
    try:
        ast.parse(output.code_executable)
    except SyntaxError:
        return 0.0
    try:
        compile(output.code_executable, "<organ-output>", "exec")
    except Exception:
        return 0.2
    return 1.0


def required_fields(example: TrainingExample) -> float:
    output = example.organ_output
    required = ["intent", "exec_ready", "tools_needed", "steps", "response"]
    if output.intent == "code":
        required.append("code_executable")
    if output.intent == "debug":
        required.extend(["error", "code_executable"])
    if output.intent in {"classify", "evaluate"}:
        required.append("expected_schema")
    score = 0
    for field in required:
        value = getattr(output, field)
        if field == "tools_needed":
            score += 1
        elif value not in (None, "", []):
            score += 1
    return score / len(required)


def intent_valid(example: TrainingExample) -> float:
    allowed = INTENT_BY_ORGAN.get(example.target_organ, set())
    return 1.0 if example.organ_output.intent in allowed else 0.0


def exec_consistency(output: OrganOutput) -> float:
    if output.exec_ready and output.tools_needed:
        return 1.0
    if not output.exec_ready and not output.code_executable:
        return 0.5
    return 0.0


def token_economy(output: OrganOutput) -> float:
    count = _token_count([output.response, *output.steps])
    if count <= 40:
        return 1.0
    if count >= 150:
        return 0.0
    if count <= 80:
        return 1.0 - ((count - 40) / 40) * 0.5
    return 0.5 - ((count - 80) / 70) * 0.5


def chain_step_validity(output: OrganOutput) -> float:
    if not output.steps:
        return 0.0
    valid = 1
    previous_terms = set(_tokens(output.steps[0]))
    for step in output.steps[1:]:
        terms = set(_tokens(step))
        if previous_terms & terms:
            valid += 1
        previous_terms |= terms
    return valid / len(output.steps)


def schema_match(output: OrganOutput) -> float:
    if not output.expected_schema:
        return 0.0
    try:
        parsed = json.loads(output.response)
    except json.JSONDecodeError:
        return 0.0
    hits = sum(1 for key in output.expected_schema if key in parsed)
    return hits / len(output.expected_schema)


def coherence_score(example: TrainingExample) -> float:
    query_terms = set(_tokens(example.query))
    output_terms = set(_tokens(example.organ_output.response))
    if not query_terms or not output_terms:
        return 0.0
    overlap = len(query_terms & output_terms) / len(query_terms | output_terms)
    return min(1.0, 0.55 + overlap)


def score_example(example: TrainingExample) -> dict[str, float]:
    output = example.organ_output
    raw = {
        "code_executable_pass": code_executable_pass(output),
        "required_fields": required_fields(example),
        "intent_valid": intent_valid(example),
        "exec_consistency": exec_consistency(output),
        "token_economy": token_economy(output),
        "chain_step_validity": chain_step_validity(output),
        "schema_match": schema_match(output),
        "coherence_score": coherence_score(example),
    }
    weights = REWARD_WEIGHTS[example.target_organ]
    raw["weighted_total"] = sum(raw[name] * weight for name, weight in weights.items())
    return raw
