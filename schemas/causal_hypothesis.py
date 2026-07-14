from pydantic import BaseModel, Field


class CausalHypothesis(BaseModel):
    hypothesis_id: str
    lens: str
    claim: str
    drivers: list[str] = Field(default_factory=list)
    mediators: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    affected_agents: list[str] = Field(default_factory=list)
    time_scale: str
    confidence: float = Field(ge=0.0, le=1.0)
