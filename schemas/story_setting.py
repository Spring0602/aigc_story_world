from dataclasses import dataclass, field


@dataclass
class StorySetting:
    genre: str
    theme: str
    tone: list[str] = field(default_factory=list)
    protagonist_brief: str = ""
    initial_location: str = ""
    initial_time: str = ""
    core_incident: str = ""
    target_audience: str = ""
    visual_style: str = ""

