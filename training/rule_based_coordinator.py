from __future__ import annotations

from dataclasses import dataclass


ORGANS = {
    "code": "code-organ",
    "debug": "debug-organ",
    "classify": "data-organ",
    "retrieve": "data-organ",
    "evaluate": "data-organ",
    "reason": "reason-organ",
    "plan": "reason-organ",
    "summarize": "synthesis-organ",
    "handoff": "synthesis-organ",
    "route": "coordinator-organ",
}

TOOLS = {
    "code": ["python-code-runner", "query_graph"],
    "debug": ["python-code-runner", "query_graph", "get_diagnostics_for_file"],
    "classify": ["query_graph"],
    "retrieve": ["query_graph", "search_graph"],
    "evaluate": ["query_graph"],
    "reason": ["query_graph", "query-docs"],
    "plan": ["query_graph"],
    "summarize": [],
    "handoff": [],
    "route": [],
}


@dataclass(frozen=True)
class Route:
    intent: str
    organ: str
    organ_chain: list[str]
    tools_needed: list[str]
    confidence: float

    def as_dict(self) -> dict:
        return {
            "intent": self.intent,
            "organ": self.organ,
            "organ_chain": self.organ_chain,
            "tools_needed": self.tools_needed,
            "confidence": self.confidence,
        }


def classify(query: str) -> dict:
    text = query.lower()

    if "which organ" in text or "organ chain" in text or "should handle" in text:
        intent = "route"
    elif "handoff" in text or "restore gemini quota" in text or "human" in text:
        intent = "handoff"
    elif "classify" in text or "category" in text:
        intent = "classify"
    elif "summarize" in text or "summary" in text:
        intent = "summarize"
    elif "evaluate" in text or "satisfies" in text or "validates" in text:
        intent = "evaluate"
    elif "find" in text or "retrieve" in text or "ast neighbors" in text or "context" in text:
        intent = "retrieve"
    elif "traceback" in text or "error" in text or "fails" in text or "diagnose" in text or "fix" in text:
        intent = "debug"
    elif "plan" in text or "steps to" in text or "without running" in text:
        intent = "plan"
    elif "reason" in text or "whether" in text or "tradeoff" in text:
        intent = "reason"
    elif "add" in text or "write" in text or "helper" in text or "python" in text:
        intent = "code"
    else:
        intent = "route"

    organ = ORGANS[intent]
    return Route(
        intent=intent,
        organ=organ,
        organ_chain=[organ, "gate-organ"] if organ != "coordinator-organ" else [organ],
        tools_needed=TOOLS[intent],
        confidence=0.9,
    ).as_dict()
