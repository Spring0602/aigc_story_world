from typing import Literal

from pydantic import BaseModel, Field, model_validator


class FabulaEvent(BaseModel):
    fabula_event_id: str
    world_event_id: str
    step: int = Field(ge=1)
    timestamp: str
    source_state_id: str
    target_state_id: str
    summary: str
    visibility: str
    actor_ids: list[str] = Field(default_factory=list)
    action_ids: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    cause_ids: list[str] = Field(default_factory=list)
    effect_paths: list[str] = Field(default_factory=list)
    provenance_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    source_belief_ids: list[str] = Field(default_factory=list)


class Fabula(BaseModel):
    fabula_id: str
    initial_state_id: str
    final_state_id: str
    state_ids: list[str] = Field(min_length=2)
    events: list[FabulaEvent] = Field(min_length=1)
    chronology_valid: bool
    causality_preserved: bool

    @model_validator(mode="after")
    def validate_chronology(self) -> "Fabula":
        steps = [item.step for item in self.events]
        if steps != sorted(steps):
            raise ValueError("fabula events must remain in chronological order")
        return self


NarrativeFunction = Literal[
    "revelation",
    "decision",
    "confrontation",
    "relationship_shift",
    "turning_point",
    "thematic_reinforcement",
    "visual_emphasis",
]


class NarrativePlanItem(BaseModel):
    fabula_event_id: str
    importance_assessment_id: str
    importance_score: float = Field(ge=0.0, le=1.0)
    narrative_function: NarrativeFunction
    selection_reason: str


class NarrativePlan(BaseModel):
    narrative_plan_id: str
    fabula_id: str
    selection_threshold: float = Field(ge=0.0, le=1.0)
    selected_items: list[NarrativePlanItem] = Field(min_length=1)
    omitted_fabula_event_ids: list[str] = Field(default_factory=list)
    planner_rationale: str


class Syuzhet(BaseModel):
    syuzhet_id: str
    narrative_plan_id: str
    arrangement: Literal["chronological", "nonlinear"] = "chronological"
    ordered_fabula_event_ids: list[str] = Field(min_length=1)
    ordering_rationale: str


class Focalization(BaseModel):
    focalization_id: str
    syuzhet_id: str
    fabula_event_id: str
    mode: Literal["third_person_limited", "internal", "external"]
    focal_agent_id: str
    observation_ids: list[str] = Field(default_factory=list)
    character_known_information_ids: list[str] = Field(default_factory=list)
    audience_information_ids: list[str] = Field(default_factory=list)
    withheld_information_ids: list[str] = Field(default_factory=list)
    audience_knows_character_does_not: list[str] = Field(default_factory=list)
    character_knows_audience_does_not: list[str] = Field(default_factory=list)
    rationale: str


class StoryOutput(BaseModel):
    story_output_id: str
    fabula_id: str
    narrative_plan_id: str
    syuzhet_id: str
    focalization_ids: list[str] = Field(min_length=1)
    narrative_event_ids: list[str] = Field(min_length=1)
    narrative_beat_ids: list[str] = Field(min_length=1)
    ordered_summaries: list[str] = Field(min_length=1)
    source_state_ids: list[str] = Field(min_length=2)
    rendered_text: str = Field(min_length=1)
    rendering_mode: str = "grounded_structured_narrative"
