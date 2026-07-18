from typing import Literal

from pydantic import BaseModel, Field


TimeScale = Literal["seconds", "minutes", "hours", "days", "weeks", "months", "years", "generations"]


class CausalHypothesis(BaseModel):
    hypothesis_id: str
    lens: str
    claim: str
    drivers: list[str] = Field(default_factory=list)
    mediators: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    affected_agents: list[str] = Field(default_factory=list)
    time_scale: TimeScale
    confidence: float = Field(ge=0.0, le=1.0)
