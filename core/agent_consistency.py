from schemas import CandidateFuture, SubjectiveWorldModel


class AgentConsistency:
    def score(self, future: CandidateFuture, subjective_models: list[SubjectiveWorldModel]) -> float:
        models = {model.agent_id: model for model in subjective_models}
        scores: list[float] = []
        for action in future.agent_actions:
            model = models.get(action.agent_id)
            if model is None:
                continue
            value_score = model.values.get("truth", 0.5)
            if "confront" in action.action:
                value_score -= model.epistemology.get("trust_authority", 0.5) * 0.3
            if "secretly" in action.action:
                value_score += model.epistemology.get("trust_data", 0.5) * 0.2
            scores.append(min(1.0, max(0.0, value_score)))
        return sum(scores) / len(scores) if scores else 0.5
