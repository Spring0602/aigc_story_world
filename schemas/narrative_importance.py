from typing import ClassVar, Literal

from pydantic import BaseModel, Field, model_validator


NARRATIVE_IMPORTANCE_WEIGHTS = {
    "conflict_change": 0.16,
    "information_gain": 0.18,
    "character_decision": 0.18,
    "relationship_change": 0.12,
    "irreversibility": 0.14,
    "theme_relevance": 0.12,
    "visual_potential": 0.10,
}


class NarrativeImportanceBreakdown(BaseModel):
    weights: ClassVar[dict[str, float]] = NARRATIVE_IMPORTANCE_WEIGHTS

    conflict_change: float = Field(ge=0.0, le=1.0)
    information_gain: float = Field(ge=0.0, le=1.0)
    character_decision: float = Field(ge=0.0, le=1.0)
    relationship_change: float = Field(ge=0.0, le=1.0)
    irreversibility: float = Field(ge=0.0, le=1.0)
    theme_relevance: float = Field(ge=0.0, le=1.0)
    visual_potential: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_weighted_score(self) -> "NarrativeImportanceBreakdown":
        expected = round(
            sum(
                getattr(self, field) * weight
                for field, weight in self.weights.items()
            ),
            3,
        )
        if abs(self.weighted_score - expected) > 0.001:
            raise ValueError(
                "weighted_score must match narrative importance dimensions"
            )
        return self


class NarrativeImportanceAssessment(BaseModel):
    assessment_id: str
    step: int = Field(ge=1)
    source_event_id: str
    source_fabula_event_id: str | None = None
    source_future_id: str
    source_future_evaluation_id: str | None = None
    source_state_id: str
    target_state_id: str
    importance_band: Literal["low", "medium", "high"]
    score_breakdown: NarrativeImportanceBreakdown
    action_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    provenance_ids: list[str] = Field(default_factory=list)
    state_change_paths: list[str] = Field(default_factory=list)
    dimension_rationales: dict[str, str] = Field(default_factory=dict)
    rationale: str
