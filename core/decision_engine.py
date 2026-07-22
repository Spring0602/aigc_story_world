from schemas import (
    Action,
    BeliefAboutOther,
    BeliefState,
    CandidateFuture,
    Decision,
    Interpretation,
    SubjectiveWorldModel,
    ValueAssessment,
)


class DecisionEngine:
    def decide(
        self,
        candidate_futures: list[CandidateFuture],
        future_scores: dict[str, float],
        subjective_models: list[SubjectiveWorldModel],
        belief_states: list[BeliefState],
        interpretations: list[Interpretation],
        other_models: list[BeliefAboutOther],
        step: int,
    ) -> tuple[CandidateFuture, list[ValueAssessment], list[Decision]]:
        models = {model.agent_id: model for model in subjective_models}
        latest_belief_state = {item.agent_id: item for item in belief_states}
        latest_interpretation = {item.agent_id: item for item in interpretations}
        other_models_by_observer: dict[str, list[BeliefAboutOther]] = {}
        for item in other_models:
            other_models_by_observer.setdefault(item.observer_agent_id, []).append(item)
        alternatives = sorted(
            {
                action.action
                for future in candidate_futures
                for action in future.agent_actions
            }
        )
        assessments: list[ValueAssessment] = []
        assessments_by_future: dict[str, list[ValueAssessment]] = {}

        sequence = 0
        for future in candidate_futures:
            future_assessments: list[ValueAssessment] = []
            for proposed_action in future.agent_actions:
                sequence += 1
                model = models[proposed_action.agent_id]
                belief_state = latest_belief_state[proposed_action.agent_id]
                assessment = self._assess_values(
                    model,
                    belief_state,
                    proposed_action.action,
                    value_assessment_id=f"value_{step:03d}_{sequence:03d}",
                )
                assessments.append(assessment)
                future_assessments.append(assessment)
            assessments_by_future[future.future_id] = future_assessments

        def decision_score(future: CandidateFuture) -> float:
            future_assessments = assessments_by_future[future.future_id]
            value_score = (
                sum(item.score for item in future_assessments) / len(future_assessments)
                if future_assessments
                else 0.5
            )
            social_adjustments = [
                self._other_model_adjustment(
                    action.action,
                    other_models_by_observer.get(action.agent_id, []),
                )
                for action in future.agent_actions
            ]
            social_adjustment = (
                sum(social_adjustments) / len(social_adjustments)
                if social_adjustments
                else 0.0
            )
            return (
                (future_scores[future.future_id] * 0.6)
                + (value_score * 0.3)
                + (social_adjustment * 0.1)
            )

        selected_future = max(candidate_futures, key=decision_score)
        decisions: list[Decision] = []
        selected_assessments = assessments_by_future[selected_future.future_id]
        for decision_sequence, (proposed_action, assessment) in enumerate(
            zip(selected_future.agent_actions, selected_assessments),
            start=1,
        ):
            agent_id = proposed_action.agent_id
            belief_state = latest_belief_state[agent_id]
            interpretation = latest_interpretation[agent_id]
            relevant_other_models = other_models_by_observer.get(agent_id, [])
            other_model_adjustment = self._other_model_adjustment(
                proposed_action.action,
                relevant_other_models,
            )
            decision = Decision(
                decision_id=f"decision_{step:03d}_{decision_sequence:03d}",
                agent_id=agent_id,
                step=step,
                belief_state_id=belief_state.belief_state_id,
                interpretation_id=interpretation.interpretation_id,
                value_assessment_id=assessment.value_assessment_id,
                selected_action=proposed_action.action,
                alternative_actions=[item for item in alternatives if item != proposed_action.action],
                supporting_belief_ids=belief_state.belief_ids,
                source_observation_ids=interpretation.observation_ids,
                other_model_ids=[item.other_model_id for item in relevant_other_models],
                other_model_adjustment=other_model_adjustment,
                rationale=(
                    f"{interpretation.meaning}; action aligns with "
                    f"{', '.join(assessment.dominant_values) or 'default values'}; "
                    f"other-model adjustment={other_model_adjustment:.3f}."
                ),
                confidence=min(
                    1.0,
                    max(
                        0.0,
                        (decision_score(selected_future) * 0.6)
                        + (interpretation.confidence * 0.4),
                    ),
                ),
            )
            decisions.append(decision)
        return selected_future, assessments, decisions

    def _other_model_adjustment(
        self,
        action: str,
        other_models: list[BeliefAboutOther],
    ) -> float:
        adjustment = 0.0
        for other_model in other_models:
            prediction = other_model.predicted_action
            confidence = other_model.confidence
            if prediction == "discourage public confrontation":
                if "confront" in action:
                    adjustment -= 0.2 * confidence
                elif "help" in action:
                    adjustment -= 0.1 * confidence
                elif "secretly" in action:
                    adjustment += 0.08 * confidence
            elif prediction == "support further investigation":
                if "help" in action or "secretly" in action:
                    adjustment += 0.12 * confidence
            elif prediction == "withhold judgment" and "confront" in action:
                adjustment -= 0.08 * confidence
        return min(1.0, max(-1.0, adjustment))

    def _assess_values(
        self,
        model: SubjectiveWorldModel,
        belief_state: BeliefState,
        action: str,
        value_assessment_id: str,
    ) -> ValueAssessment:
        relevant_names = self._relevant_values(action)
        contributions = {
            name: model.values[name].base_weight
            for name in relevant_names
            if name in model.values
        }
        score = sum(contributions.values()) / len(contributions) if contributions else 0.5
        dominant = [
            name
            for name, weight in sorted(contributions.items(), key=lambda item: item[1], reverse=True)
            if weight >= 0.6
        ]
        return ValueAssessment(
            value_assessment_id=value_assessment_id,
            agent_id=model.agent_id,
            belief_state_id=belief_state.belief_state_id,
            action=action,
            value_contributions=contributions,
            dominant_values=dominant,
            score=score,
        )

    def _relevant_values(self, action: str) -> tuple[str, ...]:
        if "secretly" in action:
            return ("truth", "freedom")
        if "confront" in action:
            return ("truth", "freedom", "safety")
        if "help" in action:
            return ("truth", "safety")
        if "delay" in action:
            return ("safety", "order")
        return ("truth", "safety", "freedom", "order")


class ActionExecutor:
    def execute(self, decisions: list[Decision]) -> list[Action]:
        return [
            Action(
                action_id=f"action_{decision.step:03d}_{sequence:03d}",
                decision_id=decision.decision_id,
                agent_id=decision.agent_id,
                action=decision.selected_action,
                step=decision.step,
                status="executed",
            )
            for sequence, decision in enumerate(decisions, start=1)
        ]
