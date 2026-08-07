from core.narrative_importance import NarrativeImportance
from schemas import (
    CandidateFuture,
    FabulaEvent,
    Focalization,
    NarrativeEvent,
    NarrativeImportanceAssessment,
    NarrativePlan,
    ObjectiveWorldState,
    SubjectiveWorldModel,
    Syuzhet,
)


class NarrativeEngine:
    def __init__(self) -> None:
        self.importance = NarrativeImportance()

    def express(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        selected_future: CandidateFuture,
        subjective_models: list[SubjectiveWorldModel],
        importance_assessment: NarrativeImportanceAssessment | None = None,
    ) -> NarrativeEvent:
        importance_score = (
            importance_assessment.score_breakdown.weighted_score
            if importance_assessment
            else self.importance.score(selected_future)
        )
        return NarrativeEvent(
            narrative_event_id=f"nar_{new_state.step:03d}",
            source_future_id=selected_future.future_id,
            source_event_id=(
                importance_assessment.source_event_id
                if importance_assessment
                else None
            ),
            importance_assessment_id=(
                importance_assessment.assessment_id
                if importance_assessment
                else None
            ),
            focal_agent="lin_xia",
            summary=selected_future.summary,
            narrative_importance=importance_score,
            revealed_information=["林夏观察到 DNS 请求重定向", "学校正在进行网络安全升级"],
            hidden_information=["检测系统的真实功能边界"],
            emotional_focus=["curiosity", "fear"],
            visual_core="电脑终端中不断刷新的异常网络记录",
        )

    def express_planned(
        self,
        state: ObjectiveWorldState,
        fabula_event: FabulaEvent,
        plan: NarrativePlan,
        syuzhet: Syuzhet,
        focalization: Focalization,
        importance_assessment: NarrativeImportanceAssessment,
        subjective_models: list[SubjectiveWorldModel],
    ) -> NarrativeEvent:
        information_by_id = {
            item.info_id: item.content
            for item in [*state.public_information, *state.hidden_facts]
        }
        focal_model = next(
            (
                item
                for item in subjective_models
                if item.agent_id == focalization.focal_agent_id
            ),
            None,
        )
        emotional_focus = []
        if focal_model:
            emotional_focus = [
                name
                for name, value in sorted(
                    focal_model.emotion.model_dump().items(),
                    key=lambda item: (-item[1], item[0]),
                )
                if value > 0.05
            ][:2]
        return NarrativeEvent(
            narrative_event_id=f"nar_{fabula_event.step:03d}",
            source_future_id=importance_assessment.source_future_id,
            source_event_id=fabula_event.world_event_id,
            importance_assessment_id=importance_assessment.assessment_id,
            source_fabula_event_id=fabula_event.fabula_event_id,
            narrative_plan_id=plan.narrative_plan_id,
            syuzhet_id=syuzhet.syuzhet_id,
            focalization_id=focalization.focalization_id,
            focal_agent=focalization.focal_agent_id,
            summary=fabula_event.summary,
            narrative_importance=(
                importance_assessment.score_breakdown.weighted_score
            ),
            revealed_information=[
                information_by_id[item]
                for item in focalization.audience_information_ids
                if item in information_by_id
            ],
            hidden_information=[
                information_by_id[item]
                for item in focalization.withheld_information_ids
                if item in information_by_id
            ],
            emotional_focus=emotional_focus,
            visual_core=(
                f"{fabula_event.summary} | effects: "
                + ", ".join(fabula_event.effect_paths)
            ),
        )
