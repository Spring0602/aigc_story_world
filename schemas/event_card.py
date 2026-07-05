from dataclasses import dataclass, field


@dataclass
class EventCard:
    event_id: str
    step: int
    summary: str
    stage: str
    cause: str
    effect: str
    involved_characters: list[str] = field(default_factory=list)
    location: str = ""
    tension_change: str = ""
    new_clues: list[str] = field(default_factory=list)
    new_conflicts: list[str] = field(default_factory=list)
    state_changes: dict[str, str] = field(default_factory=dict)

