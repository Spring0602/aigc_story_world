from typing import Any

from pydantic import BaseModel, Field

from schemas.common import EvidenceType, InformationVisibility


class Location(BaseModel):
    location_id: str
    name: str
    description: str = ""
    visibility: InformationVisibility = "public"


class InformationItem(BaseModel):
    info_id: str
    content: str
    visibility: InformationVisibility = "public"
    location_id: str | None = None
    source: str = "system"
    evidence_type: EvidenceType = "data"
    reliability: float = Field(default=0.8, ge=0.0, le=1.0)
    allowed_agent_ids: list[str] = Field(default_factory=list)
    allowed_roles: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)


class Agent(BaseModel):
    agent_id: str
    name: str
    location_id: str
    status: str = "active"
    roles: list[str] = Field(default_factory=list)
    public_attributes: dict[str, Any] = Field(default_factory=dict)


class Resource(BaseModel):
    resource_id: str
    name: str
    resource_type: str
    quantity: float = Field(default=0.0, ge=0.0)
    owner_id: str | None = None
    location_id: str | None = None
    access_rules: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source: str
    target: str
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    dependency: float = Field(default=0.0, ge=0.0, le=1.0)
    authority_asymmetry: float = Field(default=0.0, ge=0.0, le=1.0)
    emotional_attachment: float = Field(default=0.0, ge=0.0, le=1.0)
    conflict: float = Field(default=0.0, ge=0.0, le=1.0)


class Institution(BaseModel):
    institution_id: str
    name: str
    institution_type: str = ""
    authority_scope: list[str] = Field(default_factory=list)
    transparency: float = Field(default=0.5, ge=0.0, le=1.0)
    rules: list[str] = Field(default_factory=list)
    resources_controlled: list[str] = Field(default_factory=list)


class Norm(BaseModel):
    norm_id: str
    content: str
    clarity: float = Field(default=0.5, ge=0.0, le=1.0)
    institution_id: str | None = None
    sanctions: list[str] = Field(default_factory=list)


class Event(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    description: str
    visibility: InformationVisibility = "public"
    allowed_agent_ids: list[str] = Field(default_factory=list)
    participant_ids: list[str] = Field(default_factory=list)
    actor_ids: list[str] = Field(default_factory=list)
    location_id: str | None = None
    cause_ids: list[str] = Field(default_factory=list)
    effect_paths: list[str] = Field(default_factory=list)
    decision_ids: list[str] = Field(default_factory=list)
    action_ids: list[str] = Field(default_factory=list)
    source_belief_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    source_other_model_ids: list[str] = Field(default_factory=list)


class ActiveProcess(BaseModel):
    process_id: str
    type: str
    start_time: str
    time_scale: str
    drivers: list[str] = Field(default_factory=list)
    current_stage: str = ""


class StateProvenance(BaseModel):
    provenance_id: str
    step: int = Field(ge=0)
    timestamp: str
    source: str
    source_state_id: str | None = None
    target_state_id: str | None = None
    fact: str | None = None
    path: str | None = None
    old_value: Any = None
    new_value: Any = None
    cause: str = ""
    future_id: str | None = None
    action_ids: list[str] = Field(default_factory=list)
    supporting_hypothesis_ids: list[str] = Field(default_factory=list)
    source_observation_ids: list[str] = Field(default_factory=list)
    supporting_other_model_ids: list[str] = Field(default_factory=list)


class ObjectiveWorldState(BaseModel):
    state_id: str
    step: int = Field(ge=0)
    timestamp: str
    locations: dict[str, Location] = Field(default_factory=dict)
    agents: dict[str, Agent] = Field(default_factory=dict)
    resources: dict[str, Resource] = Field(default_factory=dict)
    institutions: dict[str, Institution] = Field(default_factory=dict)
    norms: dict[str, Norm] = Field(default_factory=dict)
    relationships: dict[str, Relationship] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)
    public_information: list[InformationItem] = Field(default_factory=list)
    hidden_facts: list[InformationItem] = Field(default_factory=list)
    active_processes: list[ActiveProcess] = Field(default_factory=list)
    history: list[StateProvenance] = Field(default_factory=list)
