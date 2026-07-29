from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, field_validator, model_validator


TimeScale = Literal[
    "seconds",
    "minutes",
    "hours",
    "days",
    "weeks",
    "months",
    "years",
    "generations",
]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CausalHypothesis(BaseModel):
    hypothesis_id: NonEmptyText
    lens: NonEmptyText
    claim: NonEmptyText
    drivers: list[NonEmptyText] = Field(min_length=1)
    mediators: list[NonEmptyText] = Field(min_length=1)
    constraints: list[NonEmptyText] = Field(min_length=1)
    affected_agents: list[NonEmptyText] = Field(default_factory=list)
    supporting_event_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_perception_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_belief_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_emotional_appraisal_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_stress_state_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_motivation_state_ids: list[NonEmptyText] = Field(default_factory=list)
    supporting_scarcity_assessment_ids: list[NonEmptyText] = Field(
        default_factory=list
    )
    supporting_information_asymmetry_ids: list[NonEmptyText] = Field(
        default_factory=list
    )
    supporting_role_assessment_ids: list[NonEmptyText] = Field(
        default_factory=list
    )
    supporting_norm_pressure_ids: list[NonEmptyText] = Field(
        default_factory=list
    )
    supporting_institution_power_ids: list[NonEmptyText] = Field(
        default_factory=list
    )
    time_scale: TimeScale
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator(
        "drivers",
        "mediators",
        "constraints",
        "affected_agents",
        "supporting_event_ids",
        "supporting_perception_ids",
        "supporting_belief_ids",
        "supporting_emotional_appraisal_ids",
        "supporting_stress_state_ids",
        "supporting_motivation_state_ids",
        "supporting_scarcity_assessment_ids",
        "supporting_information_asymmetry_ids",
        "supporting_role_assessment_ids",
        "supporting_norm_pressure_ids",
        "supporting_institution_power_ids",
    )
    @classmethod
    def reject_duplicates(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("causal hypothesis lists cannot contain duplicate values")
        return values

    @model_validator(mode="after")
    def require_distinct_causal_roles(self) -> "CausalHypothesis":
        role_sets = {
            "drivers": set(self.drivers),
            "mediators": set(self.mediators),
            "constraints": set(self.constraints),
        }
        overlaps = (
            role_sets["drivers"].intersection(role_sets["mediators"])
            | role_sets["drivers"].intersection(role_sets["constraints"])
            | role_sets["mediators"].intersection(role_sets["constraints"])
        )
        if overlaps:
            repeated = ", ".join(sorted(overlaps))
            raise ValueError(
                f"drivers, mediators, and constraints must have distinct roles: {repeated}"
            )
        return self
