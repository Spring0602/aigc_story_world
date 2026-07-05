from dataclasses import dataclass, field


@dataclass
class CharacterCard:
    character_id: str
    name: str
    age: int
    gender: str
    identity: str
    personality: list[str] = field(default_factory=list)
    goal: str = ""
    fear: str = ""
    secret: str = ""
    current_emotion: str = ""
    relationships: dict[str, str] = field(default_factory=dict)
    visual_features: dict[str, str] = field(default_factory=dict)

