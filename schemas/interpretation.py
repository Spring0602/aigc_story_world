from pydantic import BaseModel, Field

from schemas.subjective_world import EmotionState


class Interpretation(BaseModel):
    interpretation_id: str
    agent_id: str
    observation_ids: list[str] = Field(default_factory=list)
    belief_basis: list[str] = Field(default_factory=list)
    causal_frame: str
    meaning: str
    emotional_response: EmotionState = Field(default_factory=EmotionState)
    action_implication: str
    confidence: float = Field(ge=0.0, le=1.0)
