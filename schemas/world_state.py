from dataclasses import dataclass, field


@dataclass
class WorldState:
    state_id: str
    step: int
    current_time: str
    current_location: str
    atmosphere: str
    world_rules: list[str] = field(default_factory=list)
    characters: dict[str, dict] = field(default_factory=dict)
    known_facts: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    unresolved_conflicts: list[str] = field(default_factory=list)
    events_happened: list[str] = field(default_factory=list)
    available_locations: list[str] = field(default_factory=list)

