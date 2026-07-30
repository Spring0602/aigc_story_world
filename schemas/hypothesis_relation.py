from typing import Literal

from pydantic import BaseModel, Field, model_validator

from schemas.causal_hypothesis import CausalHypothesis


HypothesisRelationType = Literal["supports", "contradicts", "conditions"]
ResolutionStatus = Literal["reinforcing", "context_dependent", "unresolved"]


class HypothesisRelation(BaseModel):
    relation_id: str
    source_hypothesis_id: str
    target_hypothesis_id: str
    source_lens: str
    target_lens: str
    relation_type: HypothesisRelationType
    basis: list[str] = Field(min_length=1)
    shared_drivers: list[str] = Field(default_factory=list)
    affected_agents: list[str] = Field(default_factory=list)
    strength: float = Field(ge=0.0, le=1.0)
    resolution_status: ResolutionStatus

    @model_validator(mode="after")
    def require_distinct_hypotheses(self) -> "HypothesisRelation":
        if self.source_hypothesis_id == self.target_hypothesis_id:
            raise ValueError("a hypothesis cannot relate to itself")
        return self


class LensAnalysisResult(BaseModel):
    enabled_lenses: list[str] = Field(default_factory=list)
    hypotheses: list[CausalHypothesis] = Field(default_factory=list)
    relations: list[HypothesisRelation] = Field(default_factory=list)
    unresolved_conflict_ids: list[str] = Field(default_factory=list)
