from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Intent = Literal[
    "route",
    "code",
    "reason",
    "classify",
    "retrieve",
    "summarize",
    "plan",
    "debug",
    "evaluate",
    "handoff",
]

Organ = Literal[
    "code-organ",
    "reason-organ",
    "data-organ",
    "debug-organ",
    "synthesis-organ",
    "gate-organ",
    "coordinator-organ",
]


class DoCoreAIProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    temperature: float = Field(ge=0.0, le=1.0)
    precision: float = Field(ge=0.0, le=1.0)
    reasoning_depth: float = Field(ge=0.0, le=1.0)
    creativity: float = Field(ge=0.0, le=1.0)


class CoordinatorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rationalization: str = Field(description="Cognitive scratchpad to prevent XGrammar-2 logit divergence")
    intent: Intent
    organ: Organ
    organ_chain: list[Organ]
    docoreai_profile: DoCoreAIProfile
    confidence: float = Field(ge=0.0, le=1.0)
    tools_needed: list[str]

    @field_validator("organ_chain")
    @classmethod
    def organ_chain_not_empty(cls, value: list[Organ]) -> list[Organ]:
        if not value:
            raise ValueError("organ_chain must contain at least one organ")
        return value


class OrganOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    exec_ready: bool
    pytest_assertions: str | None = None
    code_executable: str | None = None
    tools_needed: list[str]
    steps: list[str]
    error: str | None = None
    output_format: Literal["text", "json", "bool", "code"] = "text"
    response: str
    expected_schema: dict[str, str] | None = None

    @model_validator(mode="after")
    def required_fields_by_intent(self) -> "OrganOutput":
        if self.intent == "code" and not self.pytest_assertions:
            raise ValueError("code intent requires pytest_assertions for Test-Driven Synthesis")
        if self.intent == "code" and not self.code_executable:
            raise ValueError("code intent requires code_executable")
        if self.intent == "debug" and not self.error:
            raise ValueError("debug intent requires error")
        if self.intent in {"reason", "plan"} and len(self.steps) < 3:
            raise ValueError(f"{self.intent} intent requires at least three steps")
        if self.intent in {"classify", "evaluate"} and self.output_format not in {"json", "bool"}:
            raise ValueError(f"{self.intent} intent requires json or bool output_format")
        if self.exec_ready and not self.tools_needed:
            raise ValueError("exec_ready outputs require tools_needed")
        return self


class TrainingExample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    query: str
    target_organ: Organ
    coordinator: CoordinatorOutput
    organ_output: OrganOutput
    ast_context: dict[str, Any] | None = None
    graphiti_context: dict[str, Any] | None = None
    notes: str

    @model_validator(mode="after")
    def coordinator_matches_target(self) -> "TrainingExample":
        if self.coordinator.organ != self.target_organ:
            raise ValueError("coordinator.organ must match target_organ")
        if self.organ_output.intent != self.coordinator.intent:
            raise ValueError("organ_output.intent must match coordinator.intent")
        return self

