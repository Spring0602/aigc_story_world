from pydantic import BaseModel, Field


class RoleAssessment(BaseModel):
    role_assessment_id: str
    agent_id: str
    step: int = Field(ge=0)
    observation_ids: list[str] = Field(default_factory=list)
    belief_state_id: str
    roles: list[str] = Field(default_factory=list)
    expected_behaviors: list[str] = Field(default_factory=list)
    role_constraint: float = Field(ge=0.0, le=1.0)
    role_conflict: float = Field(ge=0.0, le=1.0)


class NormPressureAssessment(BaseModel):
    norm_pressure_id: str
    agent_id: str
    step: int = Field(ge=0)
    observation_ids: list[str] = Field(default_factory=list)
    belief_state_id: str
    norm_id: str
    institution_id: str | None = None
    clarity: float = Field(ge=0.0, le=1.0)
    sanction_severity: float = Field(ge=0.0, le=1.0)
    compliance_pressure: float = Field(ge=0.0, le=1.0)


class InstitutionPowerAssessment(BaseModel):
    institution_power_id: str
    agent_id: str
    step: int = Field(ge=0)
    observation_ids: list[str] = Field(default_factory=list)
    belief_state_id: str
    institution_id: str
    authority_scope: list[str] = Field(default_factory=list)
    controlled_resource_ids: list[str] = Field(default_factory=list)
    transparency: float = Field(ge=0.0, le=1.0)
    resource_dependence: float = Field(ge=0.0, le=1.0)
    authority_power: float = Field(ge=0.0, le=1.0)
    power_asymmetry: float = Field(ge=0.0, le=1.0)


class SocialActionEvaluation(BaseModel):
    social_evaluation_id: str
    agent_id: str
    step: int = Field(ge=0)
    action: str
    belief_state_id: str
    role_assessment_id: str
    norm_pressure_ids: list[str] = Field(default_factory=list)
    institution_power_ids: list[str] = Field(default_factory=list)
    motivation_state_id: str | None = None
    emotional_appraisal_id: str | None = None
    bias_filter_ids: list[str] = Field(default_factory=list)
    role_alignment: float = Field(ge=0.0, le=1.0)
    norm_compliance: float = Field(ge=0.0, le=1.0)
    institutional_risk: float = Field(ge=0.0, le=1.0)
    social_support: float = Field(ge=0.0, le=1.0)
    compatibility: float = Field(ge=0.0, le=1.0)
    rationale: str


class SocialContext(BaseModel):
    role_assessments: list[RoleAssessment] = Field(default_factory=list)
    norm_pressures: list[NormPressureAssessment] = Field(default_factory=list)
    institution_powers: list[InstitutionPowerAssessment] = Field(
        default_factory=list
    )
    action_evaluations: list[SocialActionEvaluation] = Field(default_factory=list)
