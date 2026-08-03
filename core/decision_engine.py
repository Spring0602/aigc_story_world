from schemas import (
    Action,
    AgentActionDecision,
    BeliefAboutOther,
    BeliefState,
    CandidateFuture,
    Decision,
    EconomicActionEvaluation,
    EconomicContext,
    Interpretation,
    MotivationState,
    PsychologyContext,
    SocialActionEvaluation,
    SocialContext,
    StressState,
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
        psychology: PsychologyContext | None = None,
        economics: EconomicContext | None = None,
        social: SocialContext | None = None,
        action_decisions: list[AgentActionDecision] | None = None,
    ) -> tuple[CandidateFuture, list[ValueAssessment], list[Decision]]:
        models = {model.agent_id: model for model in subjective_models}
        latest_belief_state = {item.agent_id: item for item in belief_states}
        latest_interpretation = {item.agent_id: item for item in interpretations}
        motivations = {
            item.agent_id: item
            for item in (psychology.motivation_states if psychology else [])
        }
        stress_states = {
            item.agent_id: item
            for item in (psychology.stress_states if psychology else [])
        }
        emotional_appraisals = {
            item.agent_id: item
            for item in (psychology.emotional_appraisals if psychology else [])
        }
        perceptions = {
            item.agent_id: item
            for item in (psychology.perceptions if psychology else [])
        }
        economic_evaluations = {
            (item.agent_id, item.action): item
            for item in (economics.action_evaluations if economics else [])
        }
        opportunity_costs = {
            item.opportunity_cost_id: item
            for item in (economics.opportunity_costs if economics else [])
        }
        social_evaluations = {
            (item.agent_id, item.action): item
            for item in (social.action_evaluations if social else [])
        }
        other_models_by_observer: dict[str, list[BeliefAboutOther]] = {}
        for item in other_models:
            other_models_by_observer.setdefault(item.observer_agent_id, []).append(item)
        action_decisions_by_key = {
            (item.agent_id, item.action): item
            for item in (action_decisions or [])
        }
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
                    motivation=motivations.get(proposed_action.agent_id),
                    stress=stress_states.get(proposed_action.agent_id),
                    economic_evaluation=economic_evaluations.get(
                        (proposed_action.agent_id, proposed_action.action)
                    ),
                    opportunity_costs=opportunity_costs,
                    social_evaluation=social_evaluations.get(
                        (proposed_action.agent_id, proposed_action.action)
                    ),
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
            action_decision = action_decisions_by_key.get(
                (agent_id, proposed_action.action)
            )
            decision = Decision(
                decision_id=f"decision_{step:03d}_{decision_sequence:03d}",
                agent_id=agent_id,
                step=step,
                belief_state_id=belief_state.belief_state_id,
                interpretation_id=interpretation.interpretation_id,
                value_assessment_id=assessment.value_assessment_id,
                perception_id=(
                    perceptions[agent_id].perception_id
                    if agent_id in perceptions
                    else None
                ),
                emotional_appraisal_id=(
                    emotional_appraisals[agent_id].emotional_appraisal_id
                    if agent_id in emotional_appraisals
                    else None
                ),
                stress_state_id=(
                    stress_states[agent_id].stress_state_id
                    if agent_id in stress_states
                    else None
                ),
                motivation_state_id=(
                    motivations[agent_id].motivation_state_id
                    if agent_id in motivations
                    else None
                ),
                social_evaluation_id=assessment.social_evaluation_id,
                selected_action=proposed_action.action,
                alternative_actions=[item for item in alternatives if item != proposed_action.action],
                supporting_belief_ids=belief_state.belief_ids,
                source_observation_ids=interpretation.observation_ids,
                other_model_ids=[item.other_model_id for item in relevant_other_models],
                other_model_adjustment=other_model_adjustment,
                rationale=(
                    f"{interpretation.meaning}; action aligns with "
                    f"{', '.join(assessment.dominant_values) or 'default values'}; "
                    f"motivation-alignment={assessment.motivation_alignment:.3f}; "
                    f"stress-adjustment={assessment.stress_adjustment:.3f}; "
                    f"economic-utility="
                    f"{assessment.economic_utility if assessment.economic_utility is not None else 0.5:.3f}; "
                    f"social-compatibility="
                    f"{assessment.social_compatibility if assessment.social_compatibility is not None else 0.5:.3f}; "
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
                agent_action_decision_id=(
                    action_decision.action_decision_id
                    if action_decision else None
                ),
                bounded_rationality_score=(
                    action_decision.score_breakdown.weighted_score
                    if action_decision else None
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
        motivation: MotivationState | None = None,
        stress: StressState | None = None,
        economic_evaluation: EconomicActionEvaluation | None = None,
        opportunity_costs: dict | None = None,
        social_evaluation: SocialActionEvaluation | None = None,
    ) -> ValueAssessment:
        relevant_names = self._relevant_values(action)
        contributions = {
            name: model.values[name].base_weight
            for name in relevant_names
            if name in model.values
        }
        value_score = (
            sum(contributions.values()) / len(contributions)
            if contributions
            else 0.5
        )
        motivation_alignment = (
            self._motivation_alignment(action, motivation)
            if motivation
            else 0.5
        )
        stress_adjustment = (
            self._stress_adjustment(action, motivation, stress)
            if stress
            else 0.0
        )
        score = (
            self._clamp(
                (value_score * 0.7)
                + (motivation_alignment * 0.3)
                + stress_adjustment
            )
            if motivation
            else value_score
        )
        opportunity_cost = None
        if economic_evaluation is not None:
            opportunity = (opportunity_costs or {}).get(
                economic_evaluation.opportunity_cost_id
            )
            opportunity_cost = (
                opportunity.opportunity_cost if opportunity is not None else 0.0
            )
            score = self._clamp(
                (score * 0.75) + (economic_evaluation.utility * 0.25)
            )
        if social_evaluation is not None:
            score = self._clamp(
                (score * 0.8) + (social_evaluation.compatibility * 0.2)
            )
        dominant = [
            name
            for name, weight in sorted(contributions.items(), key=lambda item: item[1], reverse=True)
            if weight >= 0.6
        ]
        return ValueAssessment(
            value_assessment_id=value_assessment_id,
            agent_id=model.agent_id,
            belief_state_id=belief_state.belief_state_id,
            motivation_state_id=(
                motivation.motivation_state_id if motivation else None
            ),
            stress_state_id=stress.stress_state_id if stress else None,
            economic_evaluation_id=(
                economic_evaluation.economic_evaluation_id
                if economic_evaluation
                else None
            ),
            social_evaluation_id=(
                social_evaluation.social_evaluation_id
                if social_evaluation
                else None
            ),
            action=action,
            value_contributions=contributions,
            dominant_values=dominant,
            motivation_alignment=motivation_alignment,
            stress_adjustment=stress_adjustment,
            economic_utility=(
                economic_evaluation.utility if economic_evaluation else None
            ),
            opportunity_cost=opportunity_cost,
            social_compatibility=(
                social_evaluation.compatibility
                if social_evaluation
                else None
            ),
            score=score,
        )

    def _motivation_alignment(
        self,
        action: str,
        motivation: MotivationState,
    ) -> float:
        if action == motivation.preferred_action:
            return 1.0
        scores = {
            "verify_threat": {
                "secretly": 1.0,
                "help": 0.7,
                "confront": 0.6,
                "delay": 0.2,
            },
            "preserve_stability": {
                "delay": 1.0,
                "help": 0.7,
                "secretly": 0.35,
                "confront": 0.1,
            },
            "reduce_uncertainty": {
                "help": 1.0,
                "secretly": 0.75,
                "delay": 0.55,
                "confront": 0.15,
            },
        }[motivation.motive]
        return next(
            (score for token, score in scores.items() if token in action),
            0.5,
        )

    def _stress_adjustment(
        self,
        action: str,
        motivation: MotivationState | None,
        stress: StressState,
    ) -> float:
        if "confront" in action:
            return -0.2 * stress.level
        if motivation and motivation.motive == "verify_threat" and "secretly" in action:
            return 0.08 * stress.level
        if motivation and motivation.motive == "preserve_stability" and "delay" in action:
            return 0.06 * stress.level
        return 0.0

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))

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
