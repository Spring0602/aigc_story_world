from typing import Literal

from pydantic import BaseModel, Field


ObservationVisibility = Literal["public", "private", "role"]


class Observation(BaseModel):
    observation_id: str
    agent_id: str
    step: int = Field(ge=0)
    source: str
    content: str
    reliability: float = Field(ge=0.0, le=1.0)
    visibility: ObservationVisibility = "private"
