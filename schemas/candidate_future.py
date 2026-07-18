from typing import Any

from pydantic import BaseModel, Field

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


class CandidateFuture(BaseModel):
    future_id: str
    summary: str
    estimated_plausibility: float = Field(ge=0.0, le=1.0)
    time_horizon: TimeScale
    trigger_conditions: list[str] = Field(default_factory=list)
    supporting_hypotheses: list[str] = Field(default_factory=list)
    agent_actions: list[AgentAction] = Field(default_factory=list)
    expected_state_changes: list[StateChange] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
