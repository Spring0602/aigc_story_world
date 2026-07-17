from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator


UnitScore = Annotated[float, Field(ge=0.0, le=1.0)]
ContextModifier = Annotated[float, Field(ge=-1.0, le=1.0)]


class Belief(BaseModel):
    belief_id: str
    proposition: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    source: str = ""
    last_updated_step: int = 0


class Epistemology(BaseModel):
    trust_data: UnitScore = 0.5
    trust_authority: UnitScore = 0.5
    trust_personal_experience: UnitScore = 0.5
    trust_social_consensus: UnitScore = 0.5
    trust_intuition: UnitScore = 0.5
    tolerance_for_uncertainty: UnitScore = 0.5


class Value(BaseModel):
    base_weight: UnitScore
    context_modifiers: dict[str, ContextModifier] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def accept_weight_shorthand(cls, value: Any) -> Any:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return {"base_weight": value}
        return value

    def weight_for(self, context: str | None = None) -> float:
        modifier = self.context_modifiers.get(context, 0.0) if context else 0.0
        return min(1.0, max(0.0, self.base_weight + modifier))


class EmotionState(BaseModel):
    fear: UnitScore = 0.0
    anger: UnitScore = 0.0
    shame: UnitScore = 0.0
    curiosity: UnitScore = 0.0
    hope: UnitScore = 0.0


class SubjectiveWorldModel(BaseModel):
    agent_id: str
    knowledge: list[str] = Field(default_factory=list)
    beliefs: list[Belief] = Field(default_factory=list)
    false_beliefs: list[Belief] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    values: dict[str, Value] = Field(default_factory=dict)
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    identity: dict[str, Any] = Field(default_factory=dict)
    roles: list[str] = Field(default_factory=list)
    epistemology: Epistemology = Field(default_factory=Epistemology)
    human_nature_model: dict[str, float] = Field(default_factory=dict)
    theory_of_change: dict[str, float] = Field(default_factory=dict)
    methodology: list[str] = Field(default_factory=list)
    memory: list[str] = Field(default_factory=list)
    emotion: EmotionState = Field(default_factory=EmotionState)
    beliefs_about_others: dict[str, Any] = Field(default_factory=dict)
