from typing import Literal

from pydantic import BaseModel, Field

from schemas.subjective_world import EmotionState


StressBand = Literal["low", "moderate", "high"]
MotivationType = Literal[
    "verify_threat",
    "preserve_stability",
    "reduce_uncertainty",
]
ActionOrientation = Literal["approach", "avoidance", "mixed"]


class Perception(BaseModel):
    perception_id: str
    agent_id: str
    step: int = Field(ge=0)
    source_event_id: str
    observation_ids: list[str] = Field(default_factory=list)
    perceived_content: str
    goal_relevance: float = Field(ge=0.0, le=1.0)
    threat: float = Field(ge=0.0, le=1.0)
    controllability: float = Field(ge=0.0, le=1.0)
    ambiguity: float = Field(ge=0.0, le=1.0)
    salience: float = Field(ge=0.0, le=1.0)


class EmotionalAppraisal(BaseModel):
    emotional_appraisal_id: str
    agent_id: str
    step: int = Field(ge=0)
    perception_id: str
    belief_state_id: str
    belief_ids: list[str] = Field(default_factory=list)
    interpretation_id: str
    emotion: EmotionState
    dominant_emotion: Literal["fear", "anger", "shame", "curiosity", "hope"]
    intensity: float = Field(ge=0.0, le=1.0)


class StressState(BaseModel):
    stress_state_id: str
    agent_id: str
    step: int = Field(ge=0)
    emotional_appraisal_id: str
    perception_id: str
    stressors: list[str] = Field(default_factory=list)
    level: float = Field(ge=0.0, le=1.0)
    band: StressBand
    coping_capacity: float = Field(ge=0.0, le=1.0)


class MotivationState(BaseModel):
    motivation_state_id: str
    agent_id: str
    step: int = Field(ge=0)
    stress_state_id: str
    emotional_appraisal_id: str
    belief_state_id: str
    motive: MotivationType
    target: str
    orientation: ActionOrientation
    intensity: float = Field(ge=0.0, le=1.0)
    supporting_goals: list[str] = Field(default_factory=list)
    preferred_action: str


class PsychologyContext(BaseModel):
    perceptions: list[Perception] = Field(default_factory=list)
    emotional_appraisals: list[EmotionalAppraisal] = Field(default_factory=list)
    stress_states: list[StressState] = Field(default_factory=list)
    motivation_states: list[MotivationState] = Field(default_factory=list)
