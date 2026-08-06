from pydantic import BaseModel, Field, model_validator


class SimulationStepTrace(BaseModel):
    step: int = Field(ge=1)
    source_state_id: str
    target_state_id: str
    selected_future_id: str
    selected_mechanism_type: str
    selected_action: str
    observation_ids: list[str] = Field(default_factory=list)
    belief_state_ids: list[str] = Field(default_factory=list)
    candidate_future_ids: list[str] = Field(min_length=1)
    decision_ids: list[str] = Field(min_length=1)
    action_ids: list[str] = Field(min_length=1)
    event_ids: list[str] = Field(min_length=1)
    state_change_paths: list[str] = Field(min_length=1)
    provenance_ids: list[str] = Field(min_length=1)
    source_values_match: bool
    target_values_match: bool
    references_closed: bool


class MultiStepSimulationResult(BaseModel):
    simulation_id: str
    requested_steps: int = Field(ge=3, le=5)
    initial_state_id: str
    final_state_id: str
    traces: list[SimulationStepTrace] = Field(min_length=3, max_length=5)
    state_ids: list[str] = Field(min_length=4, max_length=6)
    continuity_preserved: bool
    snapshots_immutable: bool
    provenance_complete: bool
    no_noop_changes: bool
    passed: bool

    @model_validator(mode="after")
    def validate_trace_count(self) -> "MultiStepSimulationResult":
        if len(self.traces) != self.requested_steps:
            raise ValueError("trace count must equal requested simulation steps")
        if len(self.state_ids) != self.requested_steps + 1:
            raise ValueError("simulation must preserve every state snapshot")
        return self
