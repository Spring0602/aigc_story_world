from typing import Any

from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    agent_id: str
    name: str
    identity: dict[str, Any] = Field(default_factory=dict)
    roles: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    values: dict[str, Any] = Field(default_factory=dict)
    epistemology: dict[str, float] = Field(default_factory=dict)
    human_nature_model: dict[str, float] = Field(default_factory=dict)
    theory_of_change: dict[str, float] = Field(default_factory=dict)
    methodology: list[str] = Field(default_factory=list)
    physical_state: dict[str, Any] = Field(default_factory=dict)
    visual_features: dict[str, Any] = Field(default_factory=dict)
