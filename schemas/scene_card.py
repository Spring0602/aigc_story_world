from dataclasses import dataclass, field


@dataclass
class SceneCard:
    scene_id: str
    event_id: str
    location: str
    time: str
    main_action: str
    characters: list[dict] = field(default_factory=list)
    camera: dict[str, str] = field(default_factory=dict)
    lighting: str = ""
    atmosphere: str = ""
    key_objects: list[str] = field(default_factory=list)
    visual_style: str = ""
    negative_prompt_notes: list[str] = field(default_factory=list)

