from pydantic import BaseModel, Field


class NarrativeEvent(BaseModel):
    narrative_event_id: str
    source_future_id: str
    focal_agent: str
    summary: str
    narrative_importance: float = Field(ge=0.0, le=1.0)
    revealed_information: list[str] = Field(default_factory=list)
    hidden_information: list[str] = Field(default_factory=list)
    emotional_focus: list[str] = Field(default_factory=list)
    visual_core: str = ""
