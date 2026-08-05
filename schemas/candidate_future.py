from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from schemas.causal_hypothesis import TimeScale


class AgentAction(BaseModel):
    agent_id: str
    action: str


class StateChange(BaseModel):
    path: str
    old_value: Any = None
    new_value: Any
    reason: str
    future_id: str


FutureMechanismType = Literal[
    "information_discovery",
    "social_coordination",
    "institutional_contestation",
    "process_inertia",
]


class FutureMechanism(BaseModel):
    mechanism_id: str
    mechanism_type: FutureMechanismType
    description: str
    drivers: list[str] = Field(min_length=1)
    mediators: list[str] = Field(min_length=1)
    constraints: list[str] = Field(min_length=1)
    lens_names: list[str] = Field(default_factory=list)
    source_hypothesis_ids: list[str] = Field(default_factory=list)
    source_active_process_ids: list[str] = Field(default_factory=list)


class CandidateFuture(BaseModel):
    future_id: str
    source_state_id: str = ""
    summary: str
    estimated_plausibility: float = Field(ge=0.0, le=1.0)
    time_horizon: TimeScale
    trigger_conditions: list[str] = Field(default_factory=list)
    supporting_hypotheses: list[str] = Field(default_factory=list)
    agent_actions: list[AgentAction] = Field(default_factory=list)
    expected_state_changes: list[StateChange] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    source_possible_world_ids: list[str] = Field(default_factory=list)
    source_belief_distribution_ids: list[str] = Field(default_factory=list)
    belief_plausibility: float = Field(default=0.5, ge=0.0, le=1.0)
    mechanism: FutureMechanism | None = None
    opposing_hypotheses: list[str] = Field(default_factory=list)
    generation_rationale: str = ""
    source_action_decision_ids: list[str] = Field(default_factory=list)
    bounded_rationality_score: float = Field(default=0.5, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_mechanism_references(self) -> "CandidateFuture":
        if self.mechanism is not None and set(
            self.mechanism.source_hypothesis_ids
        ) != set(self.supporting_hypotheses):
            raise ValueError(
                "mechanism source hypotheses must match future support"
            )
        if any(
            change.future_id != self.future_id
            for change in self.expected_state_changes
        ):
            raise ValueError("state changes must reference their candidate future")
        return self
