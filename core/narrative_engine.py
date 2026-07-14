from core.narrative_importance import NarrativeImportance
from schemas import CandidateFuture, NarrativeEvent, ObjectiveWorldState, SubjectiveWorldModel


class NarrativeEngine:
    def __init__(self) -> None:
        self.importance = NarrativeImportance()

    def express(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        selected_future: CandidateFuture,
        subjective_models: list[SubjectiveWorldModel],
    ) -> NarrativeEvent:
        return NarrativeEvent(
            narrative_event_id=f"nar_{new_state.step:03d}",
            source_future_id=selected_future.future_id,
            focal_agent="lin_xia",
            summary=selected_future.summary,
            narrative_importance=self.importance.score(selected_future),
            revealed_information=["林夏观察到 DNS 请求重定向", "学校正在进行网络安全升级"],
            hidden_information=["检测系统的真实功能边界"],
            emotional_focus=["curiosity", "fear"],
            visual_core="电脑终端中不断刷新的异常网络记录",
        )
