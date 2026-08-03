from pydantic import BaseModel, Field, model_validator


class ActionScoreBreakdown(BaseModel):
    belief_compatibility: float = Field(ge=0.0, le=1.0)
    possible_world_compatibility: float = Field(ge=0.0, le=1.0)
    goal_compatibility: float = Field(ge=0.0, le=1.0)
    value_compatibility: float = Field(ge=0.0, le=1.0)
    emotional_compatibility: float = Field(ge=0.0, le=1.0)
    motivation_compatibility: float = Field(ge=0.0, le=1.0)
    other_model_compatibility: float = Field(ge=0.0, le=1.0)
    constraint_satisfaction: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)


class AgentActionDecision(BaseModel):
    action_decision_id: str
    agent_id: str
    step: int = Field(ge=0)
    action: str
    information_boundary_id: str
    information_coverage: float = Field(ge=0.0, le=1.0)
    belief_state_id: str
    dominant_possible_world_belief_id: str
    evaluated_possible_world_id: str
    belief_distribution_id: str
    emotional_appraisal_id: str | None = None
    motivation_state_id: str | None = None
    supporting_observation_ids: list[str] = Field(default_factory=list)
    supporting_belief_ids: list[str] = Field(default_factory=list)
    supporting_goals: list[str] = Field(default_factory=list)
    supporting_values: list[str] = Field(default_factory=list)
    other_model_ids: list[str] = Field(default_factory=list)
    constraint_ids: list[str] = Field(default_factory=list)
    supporting_hypothesis_ids: list[str] = Field(default_factory=list)
    opposing_hypothesis_ids: list[str] = Field(default_factory=list)
    score_breakdown: ActionScoreBreakdown
    satisficing_threshold: float = Field(ge=0.0, le=1.0)
    consideration_rank: int = Field(ge=1)
    is_satisficing: bool
    is_preferred: bool = False
    rationale: str

    @model_validator(mode="after")
    def validate_satisficing_flag(self) -> "AgentActionDecision":
        expected = self.score_breakdown.weighted_score >= self.satisficing_threshold
        if self.is_satisficing != expected:
            raise ValueError("satisficing flag must agree with score and threshold")
        if self.is_preferred and self.consideration_rank != 1:
            raise ValueError("only the first-ranked action can be preferred")
        return self
