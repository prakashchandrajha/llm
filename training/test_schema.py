from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from rewards import score_example
from schema import TrainingExample


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples" / "ground_truth.jsonl"
EXPECTED_ORGANS = {
    "code-organ",
    "reason-organ",
    "data-organ",
    "debug-organ",
    "synthesis-organ",
}


def load_examples() -> list[TrainingExample]:
    examples: list[TrainingExample] = []
    with EXAMPLES.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                examples.append(TrainingExample.model_validate_json(line))
            except Exception as exc:
                raise AssertionError(f"{EXAMPLES}:{line_no}: {exc}") from exc
    return examples


def main() -> None:
    examples = load_examples()
    if len(examples) != 150:
        raise AssertionError(f"expected 150 examples, got {len(examples)}")

    per_organ = Counter(example.target_organ for example in examples)
    if set(per_organ) != EXPECTED_ORGANS:
        raise AssertionError(f"unexpected organs: {sorted(per_organ)}")
    for organ in EXPECTED_ORGANS:
        if per_organ[organ] != 30:
            raise AssertionError(f"{organ} expected 30 examples, got {per_organ[organ]}")

    ast_counts = Counter(example.target_organ for example in examples if example.ast_context)
    for organ in EXPECTED_ORGANS:
        if ast_counts[organ] != 6:
            raise AssertionError(f"{organ} expected 6 ast_context examples, got {ast_counts[organ]}")
    if sum(ast_counts.values()) != 30:
        raise AssertionError(f"expected 30 total ast_context examples, got {sum(ast_counts.values())}")

    score_totals: dict[str, list[float]] = defaultdict(list)
    code_exec_pass = 0
    for example in examples:
        scores = score_example(example)
        if scores["required_fields"] != 1.0:
            raise AssertionError(f"{example.id} failed required_fields: {scores}")
        if scores["intent_valid"] != 1.0:
            raise AssertionError(f"{example.id} failed intent_valid: {scores}")
        if example.target_organ == "code-organ" and scores["code_executable_pass"] > 0.5:
            code_exec_pass += 1
        score_totals[example.target_organ].append(scores["weighted_total"])

    if code_exec_pass < 20:
        raise AssertionError(f"expected at least 20 code examples above 0.5 executable score, got {code_exec_pass}")

    summary = {
        organ: round(sum(values) / len(values), 4)
        for organ, values in sorted(score_totals.items())
    }
    print(json.dumps({
        "examples": len(examples),
        "per_organ": dict(sorted(per_organ.items())),
        "ast_context_per_organ": dict(sorted(ast_counts.items())),
        "code_examples_executable_above_0_5": code_exec_pass,
        "average_weighted_scores": summary,
    }, indent=2))


if __name__ == "__main__":
    main()

