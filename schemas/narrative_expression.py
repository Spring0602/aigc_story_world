from typing import Literal

from pydantic import BaseModel, Field, model_validator

from schemas.narrative_structure import NarrativeFunction


NarrativeEffect = Literal[
    "alignment",
    "suspense",
    "mystery",
    "dramatic_irony",
]


class InformationEffect(BaseModel):
    effect_id: str
    focalization_id: str
    shared_information_ids: list[str] = Field(default_factory=list)
    audience_only_information_ids: list[str] = Field(default_factory=list)
    character_only_information_ids: list[str] = Field(default_factory=list)
    withheld_information_ids: list[str] = Field(default_factory=list)
    dominant_effect: NarrativeEffect
    tension_score: float = Field(ge=0.0, le=1.0)
    rationale: str

    @model_validator(mode="after")
    def validate_information_partitions(self) -> "InformationEffect":
        partitions = (
            self.shared_information_ids,
            self.audience_only_information_ids,
            self.character_only_information_ids,
            self.withheld_information_ids,
        )
        seen: set[str] = set()
        for partition in partitions:
            values = set(partition)
            if len(values) != len(partition):
                raise ValueError("information partitions cannot contain duplicates")
            if seen & values:
                raise ValueError("information partitions must be disjoint")
            seen |= values

        expected = "alignment"
        if self.withheld_information_ids:
            expected = "suspense"
        if self.character_only_information_ids:
            expected = "mystery"
        if self.audience_only_information_ids:
            expected = "dramatic_irony"
        if self.dominant_effect != expected:
            raise ValueError(
                "dominant effect must follow the represented information gap"
            )
        expected_score = round(
            min(
                1.0,
                (
                    len(self.withheld_information_ids)
                    + 1.25 * len(self.character_only_information_ids)
                    + 1.5 * len(self.audience_only_information_ids)
                )
                / max(1, len(seen)),
            ),
            3,
        )
        if abs(self.tension_score - expected_score) > 1e-9:
            raise ValueError("tension score does not match information partitions")
        return self


class NarrativeBeat(BaseModel):
    narrative_beat_id: str
    sequence: int = Field(ge=1)
    narrative_event_id: str
    source_event_id: str
    source_fabula_event_id: str
    narrative_plan_id: str
    syuzhet_id: str
    focalization_id: str
    focal_agent_id: str
    narrative_function: NarrativeFunction
    information_effect: InformationEffect
    source_information_ids: list[str] = Field(default_factory=list)
    emotional_focus: list[str] = Field(default_factory=list)
    action_text: str
    perception_text: str = ""
    internal_response_text: str = ""
    information_cue_text: str = ""
    transition_text: str = ""
    rendered_text: str

    @model_validator(mode="after")
    def validate_rendered_text(self) -> "NarrativeBeat":
        expected = "".join(
            part
            for part in (
                self.action_text,
                self.perception_text,
                self.internal_response_text,
                self.information_cue_text,
                self.transition_text,
            )
            if part
        )
        if self.rendered_text != expected:
            raise ValueError("rendered text must be composed from grounded beat parts")
        return self
