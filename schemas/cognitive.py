from typing import Literal

from pydantic import BaseModel, Field


BiasType = Literal[
    "autonomy_threat_sensitivity",
    "authority_deference",
    "evidential_skepticism",
    "ambiguity_aversion",
]
SalienceFocus = Literal["autonomy", "collective_security", "epistemic_uncertainty"]


class MentalModel(BaseModel):
    mental_model_id: str
    agent_id: str
    source_belief_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    causal_assumptions: list[str] = Field(default_factory=list)
    institutional_expectation: str
    relevant_value_weights: dict[str, float] = Field(default_factory=dict)
    uncertainty_tolerance: float = Field(ge=0.0, le=1.0)


class BiasSignal(BaseModel):
    bias_type: BiasType
    strength: float = Field(ge=0.0, le=1.0)
    rationale: str


class BiasFilterResult(BaseModel):
    bias_filter_id: str
    mental_model_id: str
    applied_biases: list[BiasSignal] = Field(default_factory=list)
    filtered_causal_frame: str
    salience_focus: SalienceFocus
    confidence_modifier: float = Field(ge=-1.0, le=1.0)
