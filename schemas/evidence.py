from typing import Literal

from pydantic import BaseModel, Field

from schemas.common import EvidenceType


EvidencePolarity = Literal["supports", "contradicts"]


class Evidence(BaseModel):
    evidence_id: str
    observation_id: str
    agent_id: str
    step: int = Field(ge=0)
    source: str
    evidence_type: EvidenceType
    content: str
    reliability: float = Field(ge=0.0, le=1.0)
    trust_basis: str
    trust_weight: float = Field(ge=0.0, le=1.0)
    strength: float = Field(ge=0.0, le=1.0)
    polarity: EvidencePolarity = "supports"
    provenance: list[str] = Field(default_factory=list)


class BayesianBeliefUpdate(BaseModel):
    update_id: str
    agent_id: str
    belief_id: str
    evidence_id: str
    prior: float = Field(ge=0.0, le=1.0)
    likelihood_e_given_true: float = Field(ge=0.0, le=1.0)
    likelihood_e_given_false: float = Field(ge=0.0, le=1.0)
    posterior: float = Field(ge=0.0, le=1.0)
    polarity: EvidencePolarity
    formula: str = "P(H|E)=P(E|H)P(H)/(P(E|H)P(H)+P(E|~H)P(~H))"


class BeliefState(BaseModel):
    belief_state_id: str
    agent_id: str
    step: int = Field(ge=0)
    belief_ids: list[str] = Field(default_factory=list)
    dominant_belief_id: str
    source_update_id: str
    uncertainty: float = Field(ge=0.0, le=1.0)
