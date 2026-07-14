from schemas import NarrativeEvent, ObjectiveWorldState, SceneCard


class SceneGenerator:
    def generate(self, state: ObjectiveWorldState, event: NarrativeEvent) -> SceneCard:
        location_id = state.agents.get(event.focal_agent, {}).get("location", "dorm")
        location = state.locations.get(location_id)
        return SceneCard(
            scene_id=f"scene_{state.step:03d}",
            narrative_event_id=event.narrative_event_id,
            location=location.name if location else location_id,
            time=state.timestamp,
            focal_agent=event.focal_agent,
            main_action="林夏在终端前保存异常流量记录，决定先秘密验证。",
            characters=[{"agent_id": "lin_xia", "pose": "leaning toward the laptop", "expression": "alert and tense"}],
            camera={"shot_type": "medium close-up", "angle": "slightly high angle", "focus": "terminal logs and Lin Xia"},
            lighting="cold blue laptop light in a dark dorm room",
            atmosphere="tense, investigative, uncertain",
            key_objects=["laptop", "terminal logs", "campus network notice"],
            negative_prompt_notes=["multiple protagonists", "daylight", "exaggerated sci-fi machinery"],
        )
