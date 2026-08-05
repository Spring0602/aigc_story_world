from typing import Any

from pydantic import BaseModel, Field, model_validator


class StateProvenance(BaseModel):
    provenance_id: str
    step: int = Field(ge=0)
    timestamp: str
    source: str
    source_state_id: str | None = None
    target_state_id: str | None = None
    fact: str | None = None
    path: str | None = None
    old_value: Any = None
    new_value: Any = None
    cause: str = ""
    future_id: str | None = None
    future_evaluation_id: str | None = None
    event_id: str | None = None
    action_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    agent_action_decision_ids: list[str] = Field(default_factory=list)
    value_assessment_ids: list[str] = Field(default_factory=list)
    supporting_hypothesis_ids: list[str] = Field(default_factory=list)
    opposing_hypothesis_ids: list[str] = Field(default_factory=list)
    hypothesis_relation_ids: list[str] = Field(default_factory=list)
    supporting_lens_names: list[str] = Field(default_factory=list)
    mechanism_id: str | None = None
    source_observation_ids: list[str] = Field(default_factory=list)
    supporting_belief_ids: list[str] = Field(default_factory=list)
    supporting_goals: list[str] = Field(default_factory=list)
    emotional_appraisal_ids: list[str] = Field(default_factory=list)
    motivation_state_ids: list[str] = Field(default_factory=list)
    constraint_ids: list[str] = Field(default_factory=list)
    supporting_other_model_ids: list[str] = Field(default_factory=list)
    source_possible_world_ids: list[str] = Field(default_factory=list)
    source_belief_distribution_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_world_transition_record(self) -> "StateProvenance":
        if self.source != "world_transition":
            return self
        required = {
            "source_state_id": self.source_state_id,
            "target_state_id": self.target_state_id,
            "path": self.path,
            "future_id": self.future_id,
            "event_id": self.event_id,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                "world transition provenance requires " + ", ".join(missing)
            )
        if self.source_state_id == self.target_state_id:
            raise ValueError("world transition must create a new state")
        if not self.action_ids:
            raise ValueError("world transition provenance requires action_ids")
        return self
