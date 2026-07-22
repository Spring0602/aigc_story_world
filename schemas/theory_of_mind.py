from typing import Literal

from pydantic import BaseModel, Field


class AttributedBelief(BaseModel):
    proposition: str
    confidence: float = Field(ge=0.0, le=1.0)


class BeliefAboutOther(BaseModel):
    other_model_id: str
    observer_agent_id: str
    target_agent_id: str
    order: Literal[2] = 2
    attributed_beliefs: list[AttributedBelief] = Field(default_factory=list)
    predicted_goals: list[str] = Field(default_factory=list)
    predicted_action: str
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    evidence_observation_ids: list[str] = Field(default_factory=list)
    evidence_event_ids: list[str] = Field(default_factory=list)
    inference_basis: list[str] = Field(default_factory=list)
    last_updated_step: int = Field(ge=0)
