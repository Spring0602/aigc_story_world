from pydantic import BaseModel, Field


class Observation(BaseModel):
    observation_id: str
    agent_id: str
    step: int
    source: str
    content: str
    reliability: float = Field(ge=0.0, le=1.0)
    visibility: str = "private"
