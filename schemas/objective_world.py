from typing import Any

from pydantic import BaseModel, Field


class Location(BaseModel):
    location_id: str
    name: str
    description: str = ""
    visibility: str = "public"


class InformationItem(BaseModel):
    info_id: str
    content: str
    visibility: str = "public"
    location_id: str | None = None
    source: str = "system"
    provenance: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source: str
    target: str
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    dependency: float = Field(default=0.0, ge=0.0, le=1.0)
    authority_asymmetry: float = Field(default=0.0, ge=0.0, le=1.0)
    emotional_attachment: float = Field(default=0.0, ge=0.0, le=1.0)
    conflict: float = Field(default=0.0, ge=0.0, le=1.0)


class ActiveProcess(BaseModel):
    process_id: str
    type: str
    start_time: str
    time_scale: str
    drivers: list[str] = Field(default_factory=list)
    current_stage: str = ""


class ObjectiveWorldState(BaseModel):
    state_id: str
    step: int
    timestamp: str
    locations: dict[str, Location] = Field(default_factory=dict)
    agents: dict[str, dict[str, Any]] = Field(default_factory=dict)
    resources: dict[str, Any] = Field(default_factory=dict)
    institutions: dict[str, Any] = Field(default_factory=dict)
    norms: dict[str, Any] = Field(default_factory=dict)
    relationships: dict[str, Relationship] = Field(default_factory=dict)
    public_information: list[InformationItem] = Field(default_factory=list)
    hidden_facts: list[InformationItem] = Field(default_factory=list)
    active_processes: list[ActiveProcess] = Field(default_factory=list)
    history: list[dict[str, Any]] = Field(default_factory=list)
