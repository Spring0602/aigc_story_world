from typing import Any

from pydantic import BaseModel, Field


class Belief(BaseModel):
    belief_id: str
    proposition: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    source: str = ""
    last_updated_step: int = 0


class SubjectiveWorldModel(BaseModel):
    agent_id: str
    knowledge: list[str] = Field(default_factory=list)
    beliefs: list[Belief] = Field(default_factory=list)
    false_beliefs: list[Belief] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    values: dict[str, Any] = Field(default_factory=dict)
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    identity: dict[str, Any] = Field(default_factory=dict)
    roles: list[str] = Field(default_factory=list)
    epistemology: dict[str, float] = Field(default_factory=dict)
    human_nature_model: dict[str, float] = Field(default_factory=dict)
    theory_of_change: dict[str, float] = Field(default_factory=dict)
    methodology: list[str] = Field(default_factory=list)
    memory: list[str] = Field(default_factory=list)
    emotion: dict[str, float] = Field(default_factory=dict)
    beliefs_about_others: dict[str, Any] = Field(default_factory=dict)
