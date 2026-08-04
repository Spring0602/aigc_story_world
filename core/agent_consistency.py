from schemas import AgentActionDecision, CandidateFuture, SubjectiveWorldModel


class AgentConsistency:
    def score(
        self,
        future: CandidateFuture,
        subjective_models: list[SubjectiveWorldModel],
        action_decisions: list[AgentActionDecision] | None = None,
    ) -> float:
        decision_score = self._decision_score(future, action_decisions or [])
        if decision_score is not None:
            return decision_score

        models = {model.agent_id: model for model in subjective_models}
        scores: list[float] = []
        for action in future.agent_actions:
            model = models.get(action.agent_id)
            if model is None:
                continue
            truth_value = model.values.get("truth")
            value_score = truth_value.base_weight if truth_value else 0.5
            if "confront" in action.action:
                value_score -= model.epistemology.trust_authority * 0.3
            if "secretly" in action.action:
                value_score += model.epistemology.trust_data * 0.2
            scores.append(min(1.0, max(0.0, value_score)))
        return sum(scores) / len(scores) if scores else 0.5

    def _decision_score(
        self,
        future: CandidateFuture,
        action_decisions: list[AgentActionDecision],
    ) -> float | None:
        source_ids = set(future.source_action_decision_ids)
        selected = [
            decision
            for decision in action_decisions
            if decision.action_decision_id in source_ids
        ]
        if not selected:
            return None

        scores = []
        for decision in selected:
            breakdown = decision.score_breakdown
            scores.append(
                sum(
                    (
                        breakdown.belief_compatibility,
                        breakdown.goal_compatibility,
                        breakdown.value_compatibility,
                        breakdown.emotional_compatibility,
                        breakdown.motivation_compatibility,
                        breakdown.other_model_compatibility,
                    )
                )
                / 6
            )
        return sum(scores) / len(scores)
