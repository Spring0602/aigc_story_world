from typing import Any

from pydantic import BaseModel, Field

from schemas.subjective_world import Epistemology, HumanNatureModel, TheoryOfChange, Value


class AgentProfile(BaseModel):
    agent_id: str
    name: str
    identity: dict[str, Any] = Field(default_factory=dict)
    roles: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    values: dict[str, Value] = Field(default_factory=dict)
    epistemology: Epistemology = Field(default_factory=Epistemology)
    human_nature_model: HumanNatureModel = Field(default_factory=HumanNatureModel)
    theory_of_change: TheoryOfChange = Field(default_factory=TheoryOfChange)
    methodology: list[str] = Field(default_factory=list)
    physical_state: dict[str, Any] = Field(default_factory=dict)
    visual_features: dict[str, Any] = Field(default_factory=dict)
