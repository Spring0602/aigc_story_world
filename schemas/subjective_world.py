from hashlib import sha1
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator


UnitScore = Annotated[float, Field(ge=0.0, le=1.0)]
ContextModifier = Annotated[float, Field(ge=-1.0, le=1.0)]


def _stable_text_id(prefix: str, text: str) -> str:
    digest = sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


class KnowledgeItem(BaseModel):
    knowledge_id: str
    content: str
    source: str = ""
    source_observation_ids: list[str] = Field(default_factory=list)
    acquired_step: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def accept_content_shorthand(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"knowledge_id": _stable_text_id("knowledge", value), "content": value}
        return value


class Belief(BaseModel):
    belief_id: str
    proposition: str
    confidence: UnitScore
    evidence: list[str] = Field(default_factory=list)
    source: str = ""
    last_updated_step: int = Field(default=0, ge=0)
    update_ids: list[str] = Field(default_factory=list)


class Uncertainty(BaseModel):
    uncertainty_id: str
    question: str
    related_belief_ids: list[str] = Field(default_factory=list)
    importance: UnitScore = 0.5
    last_updated_step: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def accept_question_shorthand(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"uncertainty_id": _stable_text_id("uncertainty", value), "question": value}
        return value


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


class HumanNatureModel(BaseModel):
    self_interest: UnitScore = 0.5
    altruism: UnitScore = 0.5
    rationality: UnitScore = 0.5
    malleability: UnitScore = 0.5
    trust_default: UnitScore = 0.5


class TheoryOfChange(BaseModel):
    material_conditions: UnitScore = 0.5
    institutions: UnitScore = 0.5
    technology: UnitScore = 0.5
    ideas: UnitScore = 0.5
    individual_leaders: UnitScore = 0.5
    social_networks: UnitScore = 0.5
    contingency: UnitScore = 0.5


class EmotionState(BaseModel):
    fear: UnitScore = 0.0
    anger: UnitScore = 0.0
    shame: UnitScore = 0.0
    curiosity: UnitScore = 0.0
    hope: UnitScore = 0.0


class SubjectiveWorldModel(BaseModel):
    agent_id: str
    knowledge: list[KnowledgeItem] = Field(default_factory=list)
    beliefs: list[Belief] = Field(default_factory=list)
    false_beliefs: list[Belief] = Field(default_factory=list)
    uncertainties: list[Uncertainty] = Field(default_factory=list)
    values: dict[str, Value] = Field(default_factory=dict)
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    identity: dict[str, Any] = Field(default_factory=dict)
    roles: list[str] = Field(default_factory=list)
    epistemology: Epistemology = Field(default_factory=Epistemology)
    human_nature_model: HumanNatureModel = Field(default_factory=HumanNatureModel)
    theory_of_change: TheoryOfChange = Field(default_factory=TheoryOfChange)
    methodology: list[str] = Field(default_factory=list)
    memory: list[str] = Field(default_factory=list)
    emotion: EmotionState = Field(default_factory=EmotionState)
    beliefs_about_others: dict[str, Any] = Field(default_factory=dict)
