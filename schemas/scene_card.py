from typing import Any

from pydantic import BaseModel, Field


class SceneCard(BaseModel):
    scene_id: str
    narrative_event_id: str
    location: str
    time: str
    focal_agent: str
    main_action: str
    characters: list[dict[str, Any]] = Field(default_factory=list)
    camera: dict[str, str] = Field(default_factory=dict)
    lighting: str = ""
    atmosphere: str = ""
    key_objects: list[str] = Field(default_factory=list)
    visual_style: str = "pixel art RPG visual novel CG, 16:9"
    negative_prompt_notes: list[str] = Field(default_factory=list)


class ImagePrompt(BaseModel):
    prompt_cn: str
    prompt_en: str
    negative_prompt_cn: str = ""
    negative_prompt_en: str = ""
