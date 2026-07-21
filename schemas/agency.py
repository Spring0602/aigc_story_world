from typing import Literal

from pydantic import BaseModel, Field


ActionStatus = Literal["selected", "executed", "failed"]


class ValueAssessment(BaseModel):
    value_assessment_id: str
    agent_id: str
    belief_state_id: str
    action: str
    value_contributions: dict[str, float] = Field(default_factory=dict)
    dominant_values: list[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)


class Decision(BaseModel):
    decision_id: str
    agent_id: str
    step: int = Field(ge=0)
    belief_state_id: str
    interpretation_id: str
    value_assessment_id: str
    selected_action: str
    alternative_actions: list[str] = Field(default_factory=list)
    supporting_belief_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class Action(BaseModel):
    action_id: str
    decision_id: str
    agent_id: str
    action: str
    step: int = Field(ge=0)
    status: ActionStatus = "selected"
