from pydantic import BaseModel, Field

from schemas.common import EvidenceType, ObservationVisibility


class Observation(BaseModel):
    observation_id: str
    information_id: str
    agent_id: str
    step: int = Field(ge=0)
    source: str
    evidence_type: EvidenceType
    content: str
    reliability: float = Field(ge=0.0, le=1.0)
    visibility: ObservationVisibility = "private"
    location_id: str | None = None
    provenance: list[str] = Field(default_factory=list)
