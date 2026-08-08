from core.narrative_importance import NarrativeImportance
from schemas import (
    CandidateFuture,
    FabulaEvent,
    Focalization,
    InformationEffect,
    NarrativeBeat,
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

    def render_beat(
        self,
        sequence: int,
        state: ObjectiveWorldState,
        narrative_event: NarrativeEvent,
        plan: NarrativePlan,
        focalization: Focalization,
    ) -> NarrativeBeat:
        if not all(
            (
                narrative_event.source_event_id,
                narrative_event.source_fabula_event_id,
                narrative_event.focalization_id,
            )
        ):
            raise ValueError("planned narrative event requires complete source links")
        if narrative_event.focalization_id != focalization.focalization_id:
            raise ValueError("narrative event and focalization must match")
        plan_item = next(
            (
                item
                for item in plan.selected_items
                if item.fabula_event_id
                == narrative_event.source_fabula_event_id
            ),
            None,
        )
        if plan_item is None:
            raise ValueError("narrative event must be selected by the plan")

        effect = self.analyze_information_effect(focalization)
        focal_agent = state.agents[focalization.focal_agent_id]
        action_text = f"第 {sequence} 步，{narrative_event.summary}"
        perception_text = ""
        if narrative_event.revealed_information:
            perception_text = (
                f"{focal_agent.name}注意到："
                f"{narrative_event.revealed_information[0]}"
            )
        internal_response_text = self._internal_response(
            focal_agent.name,
            narrative_event.emotional_focus,
        )
        information_cue_text = self._information_cue(
            focal_agent.name,
            effect.dominant_effect,
        )
        transition_text = self._transition_text(plan_item.narrative_function)
        rendered_text = "".join(
            (
                action_text,
                perception_text,
                internal_response_text,
                information_cue_text,
                transition_text,
            )
        )
        return NarrativeBeat(
            narrative_beat_id=f"beat_{sequence:03d}_{narrative_event.narrative_event_id}",
            sequence=sequence,
            narrative_event_id=narrative_event.narrative_event_id,
            source_event_id=narrative_event.source_event_id,
            source_fabula_event_id=narrative_event.source_fabula_event_id,
            narrative_plan_id=plan.narrative_plan_id,
            syuzhet_id=focalization.syuzhet_id,
            focalization_id=focalization.focalization_id,
            focal_agent_id=focalization.focal_agent_id,
            narrative_function=plan_item.narrative_function,
            information_effect=effect,
            source_information_ids=list(
                focalization.audience_information_ids
            ),
            emotional_focus=list(narrative_event.emotional_focus),
            action_text=action_text,
            perception_text=perception_text,
            internal_response_text=internal_response_text,
            information_cue_text=information_cue_text,
            transition_text=transition_text,
            rendered_text=rendered_text,
        )

    def analyze_information_effect(
        self,
        focalization: Focalization,
    ) -> InformationEffect:
        character_known = set(
            focalization.character_known_information_ids
        )
        audience_known = set(focalization.audience_information_ids)
        shared = sorted(character_known & audience_known)
        audience_only = sorted(audience_known - character_known)
        character_only = sorted(character_known - audience_known)
        withheld = sorted(focalization.withheld_information_ids)
        dominant_effect = "alignment"
        if withheld:
            dominant_effect = "suspense"
        if character_only:
            dominant_effect = "mystery"
        if audience_only:
            dominant_effect = "dramatic_irony"
        represented = set(shared + audience_only + character_only + withheld)
        tension_score = round(
            min(
                1.0,
                (
                    len(withheld)
                    + 1.25 * len(character_only)
                    + 1.5 * len(audience_only)
                )
                / max(1, len(represented)),
            ),
            3,
        )
        return InformationEffect(
            effect_id=f"information_effect_{focalization.focalization_id}",
            focalization_id=focalization.focalization_id,
            shared_information_ids=shared,
            audience_only_information_ids=audience_only,
            character_only_information_ids=character_only,
            withheld_information_ids=withheld,
            dominant_effect=dominant_effect,
            tension_score=tension_score,
            rationale=(
                "Effect is derived from the disjoint audience, character, "
                "and withheld information partitions."
            ),
        )

    def _internal_response(
        self,
        agent_name: str,
        emotions: list[str],
    ) -> str:
        if not emotions:
            return ""
        labels = {
            "anger": "愤怒",
            "curiosity": "好奇",
            "fear": "恐惧",
            "sadness": "悲伤",
            "joy": "喜悦",
            "trust": "信任",
        }
        translated = [labels.get(item, item) for item in emotions]
        return f"这让{agent_name}感到{'与'.join(translated)}。"

    def _information_cue(
        self,
        agent_name: str,
        effect: str,
    ) -> str:
        cues = {
            "alignment": "观众与角色此刻拥有相同的线索。",
            "suspense": f"与此同时，仍有信息处在{agent_name}的视野之外。",
            "mystery": f"{agent_name}掌握的部分线索暂未向观众展开。",
            "dramatic_irony": f"观众已经看见{agent_name}尚未察觉的线索。",
        }
        return cues[effect]

    def _transition_text(self, narrative_function: str) -> str:
        transitions = {
            "revelation": "线索由此浮出表面。",
            "decision": "选择已经落下。",
            "confrontation": "冲突因此变得可见。",
            "relationship_shift": "人物之间的关系随之改变。",
            "turning_point": "局面从这里转向新的阶段。",
            "thematic_reinforcement": "这一变化再次触及故事的核心议题。",
            "visual_emphasis": "这一刻构成了清晰的视觉焦点。",
        }
        return transitions[narrative_function]
