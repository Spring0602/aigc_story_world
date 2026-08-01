from math import isclose
from typing import Literal

from pydantic import BaseModel, Field, model_validator


PossibleWorldKind = Literal[
    "institutional_monitoring",
    "protective_security",
    "technical_anomaly",
]
DistributionStage = Literal["prior", "posterior"]
EvidenceCompatibility = Literal["supports", "contradicts", "neutral"]


class PossibleWorld(BaseModel):
    possible_world_id: str
    agent_id: str
    step: int = Field(ge=0)
    kind: PossibleWorldKind
    proposition: str
    assumptions: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    information_boundary_id: str


class WorldEvidenceAssessment(BaseModel):
    assessment_id: str
    possible_world_id: str
    evidence_id: str
    compatibility: EvidenceCompatibility
    likelihood: float = Field(ge=0.0, le=1.0)
    rules_out_world: bool = False
    rationale: str


class BeliefDistribution(BaseModel):
    distribution_id: str
    agent_id: str
    step: int = Field(ge=0)
    stage: DistributionStage
    information_boundary_id: str
    probabilities: dict[str, float] = Field(default_factory=dict)
    source_evidence_ids: list[str] = Field(default_factory=list)
    eliminated_world_ids: list[str] = Field(default_factory=list)
    dominant_possible_world_id: str
    uncertainty: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_probability_distribution(self) -> "BeliefDistribution":
        if not self.probabilities:
            raise ValueError("belief distribution must contain possible worlds")
        if any(value < 0.0 or value > 1.0 for value in self.probabilities.values()):
            raise ValueError("possible-world probabilities must be between 0 and 1")
        if not isclose(sum(self.probabilities.values()), 1.0, abs_tol=1e-6):
            raise ValueError("possible-world probabilities must sum to 1")
        if self.dominant_possible_world_id not in self.probabilities:
            raise ValueError("dominant possible world must be in the distribution")
        if any(self.probabilities.get(world_id) != 0.0 for world_id in self.eliminated_world_ids):
            raise ValueError("eliminated possible worlds must have zero probability")
        return self


class BayesianWorldRevision(BaseModel):
    revision_id: str
    agent_id: str
    step: int = Field(ge=0)
    prior_distribution_id: str
    posterior_distribution_id: str
    evidence_assessment_ids: list[str] = Field(default_factory=list)
    eliminated_world_ids: list[str] = Field(default_factory=list)
    normalization_constant: float = Field(gt=0.0)
    formula: str = "P(W_i|E)=P(E|W_i)P(W_i)/sum_j(P(E|W_j)P(W_j))"


class PossibleWorldBelief(BaseModel):
    belief_id: str
    agent_id: str
    step: int = Field(ge=0)
    possible_world_id: str
    proposition: str
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    belief_distribution_id: str
    source_observation_ids: list[str] = Field(default_factory=list)
    source_evidence_ids: list[str] = Field(default_factory=list)
    source_revision_id: str


class PossibleWorldContext(BaseModel):
    possible_worlds: list[PossibleWorld] = Field(default_factory=list)
    evidence_assessments: list[WorldEvidenceAssessment] = Field(default_factory=list)
    prior_distributions: list[BeliefDistribution] = Field(default_factory=list)
    revisions: list[BayesianWorldRevision] = Field(default_factory=list)
    posterior_distributions: list[BeliefDistribution] = Field(default_factory=list)
    new_beliefs: list[PossibleWorldBelief] = Field(default_factory=list)
