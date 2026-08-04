from pydantic import BaseModel, Field


class FutureScoreBreakdown(BaseModel):
    estimated_plausibility: float = Field(ge=0.0, le=1.0)
    causal_support: float = Field(ge=0.0, le=1.0)
    agent_consistency: float = Field(ge=0.0, le=1.0)
    constraint_satisfaction: float = Field(ge=0.0, le=1.0)
    state_compatibility: float = Field(ge=0.0, le=1.0)
    epistemic_compatibility: float = Field(ge=0.0, le=1.0)
    action_compatibility: float = Field(ge=0.0, le=1.0)
    compatibility: float = Field(ge=0.0, le=1.0)
    cross_lens_support: float = Field(ge=0.0, le=1.0)
    contradiction_penalty: float = Field(ge=0.0, le=1.0)
    final_score: float = Field(ge=0.0, le=1.0)


class FutureEvaluation(BaseModel):
    evaluation_id: str
    future_id: str
    source_state_id: str
    evaluated_state_id: str
    step: int = Field(ge=0)
    score_breakdown: FutureScoreBreakdown
    supporting_hypothesis_ids: list[str] = Field(default_factory=list)
    opposing_hypothesis_ids: list[str] = Field(default_factory=list)
    supporting_relation_ids: list[str] = Field(default_factory=list)
    contradicting_relation_ids: list[str] = Field(default_factory=list)
    conditioning_relation_ids: list[str] = Field(default_factory=list)
    evaluated_constraint_ids: list[str] = Field(default_factory=list)
    state_change_paths: list[str] = Field(default_factory=list)
    action_decision_ids: list[str] = Field(default_factory=list)
    rationale: str
