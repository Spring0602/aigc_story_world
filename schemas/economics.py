from pydantic import BaseModel, Field


class InformationBoundary(BaseModel):
    information_boundary_id: str
    agent_id: str
    step: int = Field(ge=0)
    source_world_step: int = Field(ge=0)
    observation_ids: list[str] = Field(default_factory=list)
    visible_information_ids: list[str] = Field(default_factory=list)
    inaccessible_information_ids: list[str] = Field(default_factory=list)
    visible_resource_ids: list[str] = Field(default_factory=list)
    access_rule_ids: list[str] = Field(default_factory=list)
    coverage: float = Field(ge=0.0, le=1.0)


class ScarcityAssessment(BaseModel):
    scarcity_assessment_id: str
    agent_id: str
    step: int = Field(ge=0)
    information_boundary_id: str
    belief_state_id: str
    resource_id: str
    available_quantity: float = Field(ge=0.0)
    access_level: float = Field(ge=0.0, le=1.0)
    physical_scarcity: float = Field(ge=0.0, le=1.0)
    access_scarcity: float = Field(ge=0.0, le=1.0)
    scarcity_level: float = Field(ge=0.0, le=1.0)
    constraint_ids: list[str] = Field(default_factory=list)


class InformationAsymmetryAssessment(BaseModel):
    information_asymmetry_id: str
    agent_id: str
    step: int = Field(ge=0)
    information_boundary_id: str
    belief_state_id: str
    informed_party_ids: list[str] = Field(default_factory=list)
    visible_information_ids: list[str] = Field(default_factory=list)
    hidden_information_ids: list[str] = Field(default_factory=list)
    institution_transparency: float = Field(ge=0.0, le=1.0)
    asymmetry_level: float = Field(ge=0.0, le=1.0)


class IncentiveAssessment(BaseModel):
    incentive_assessment_id: str
    agent_id: str
    step: int = Field(ge=0)
    information_boundary_id: str
    belief_state_id: str
    motivation_state_id: str | None = None
    action: str
    benefits: dict[str, float] = Field(default_factory=dict)
    costs: dict[str, float] = Field(default_factory=dict)
    expected_benefit: float = Field(ge=0.0, le=1.0)
    expected_cost: float = Field(ge=0.0, le=1.0)
    net_incentive: float = Field(ge=-1.0, le=1.0)


class OpportunityCostAssessment(BaseModel):
    opportunity_cost_id: str
    agent_id: str
    step: int = Field(ge=0)
    action: str
    forgone_action: str
    forgone_net_incentive: float = Field(ge=-1.0, le=1.0)
    opportunity_cost: float = Field(ge=0.0, le=1.0)


class EconomicActionEvaluation(BaseModel):
    economic_evaluation_id: str
    agent_id: str
    step: int = Field(ge=0)
    action: str
    information_boundary_id: str
    belief_state_id: str
    motivation_state_id: str | None = None
    scarcity_assessment_id: str
    information_asymmetry_id: str
    incentive_assessment_id: str
    opportunity_cost_id: str
    utility: float = Field(ge=0.0, le=1.0)
    rationale: str


class EconomicContext(BaseModel):
    information_boundaries: list[InformationBoundary] = Field(default_factory=list)
    scarcity_assessments: list[ScarcityAssessment] = Field(default_factory=list)
    information_asymmetries: list[InformationAsymmetryAssessment] = Field(
        default_factory=list
    )
    incentive_assessments: list[IncentiveAssessment] = Field(default_factory=list)
    opportunity_costs: list[OpportunityCostAssessment] = Field(default_factory=list)
    action_evaluations: list[EconomicActionEvaluation] = Field(default_factory=list)
