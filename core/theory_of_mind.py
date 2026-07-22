from schemas import (
    AttributedBelief,
    BeliefAboutOther,
    Event,
    ObjectiveWorldState,
    Observation,
    SubjectiveWorldModel,
)


class TheoryOfMindEngine:
    def infer(
        self,
        objective_state: ObjectiveWorldState,
        observations: list[Observation],
        subjective_models: list[SubjectiveWorldModel],
    ) -> tuple[list[SubjectiveWorldModel], list[BeliefAboutOther]]:
        updated_models: list[SubjectiveWorldModel] = []
        other_models: list[BeliefAboutOther] = []
        target_ids = sorted(objective_state.agents)

        for observer in subjective_models:
            updated_observer = observer.model_copy(deep=True)
            common_observations = [
                item
                for item in observations
                if item.agent_id == observer.agent_id and item.visibility == "public"
            ]
            for target_id in target_ids:
                if target_id == observer.agent_id:
                    continue
                visible_target_events = [
                    event
                    for event in objective_state.events
                    if target_id in (event.actor_ids or event.participant_ids)
                    and self._event_visible_to(event, observer.agent_id)
                ]
                other_model = self._infer_other_model(
                    observer,
                    target_id,
                    common_observations,
                    visible_target_events,
                    objective_state.step,
                )
                updated_observer.beliefs_about_others[target_id] = other_model
                other_models.append(other_model)
            updated_models.append(updated_observer)
        return updated_models, other_models

    def _infer_other_model(
        self,
        observer: SubjectiveWorldModel,
        target_id: str,
        common_observations: list[Observation],
        visible_target_events: list[Event],
        step: int,
    ) -> BeliefAboutOther:
        event_text = " ".join(event.description for event in visible_target_events)
        if any(token in event_text for token in ("正常", "安全措施", "安全升级")):
            proposition = "目标角色认为学校的升级是正常安全措施。"
            predicted_goals = ["避免冲突", "维持稳定"]
            predicted_action = "discourage public confrontation"
            confidence = min(0.95, 0.55 + (observer.epistemology.trust_social_consensus * 0.35))
        elif any(token in event_text for token in ("质疑", "调查", "验证")):
            proposition = "目标角色认为网络异常需要进一步调查。"
            predicted_goals = ["确认网络异常", "获取证据"]
            predicted_action = "support further investigation"
            confidence = min(0.95, 0.5 + (observer.epistemology.trust_personal_experience * 0.35))
        else:
            proposition = "目标角色对学校网络升级的立场尚不明确。"
            predicted_goals = ["降低不确定性"]
            predicted_action = "withhold judgment"
            confidence = 0.35

        evidence_event_ids = [event.event_id for event in visible_target_events]
        inference_basis = ["observer-visible evidence only"]
        if evidence_event_ids:
            inference_basis.append("target public behavior")
        if common_observations:
            inference_basis.append("shared public observation")
        return BeliefAboutOther(
            other_model_id=f"other_{step:03d}_{observer.agent_id}_{target_id}",
            observer_agent_id=observer.agent_id,
            target_agent_id=target_id,
            attributed_beliefs=[
                AttributedBelief(proposition=proposition, confidence=confidence)
            ],
            predicted_goals=predicted_goals,
            predicted_action=predicted_action,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            evidence_observation_ids=[item.observation_id for item in common_observations],
            evidence_event_ids=evidence_event_ids,
            inference_basis=inference_basis,
            last_updated_step=step,
        )

    def _event_visible_to(self, event: Event, observer_agent_id: str) -> bool:
        if event.visibility == "hidden":
            return False
        if event.visibility == "private":
            return observer_agent_id in event.allowed_agent_ids
        return True
