from pydantic import BaseModel, Field


class Interpretation(BaseModel):
    interpretation_id: str
    agent_id: str
    observation_ids: list[str] = Field(default_factory=list)
    claim: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_basis: list[str] = Field(default_factory=list)
