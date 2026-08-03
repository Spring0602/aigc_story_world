from core.agent_consistency import AgentConsistency
from schemas import (
    CandidateFuture,
    CausalHypothesis,
    HypothesisRelation,
    ObjectiveWorldState,
    SubjectiveWorldModel,
)


class FutureEvaluator:
    def __init__(self) -> None:
        self.agent_consistency = AgentConsistency()

    def score(
        self,
        future: CandidateFuture,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation] | None = None,
    ) -> float:
        causal_support = self.causal_support_score(
            future,
            hypotheses,
            relations or [],
        )
        consistency = self.agent_consistency.score(future, subjective_models)
        return round(
            (future.estimated_plausibility * 0.25)
            + (future.belief_plausibility * 0.10)
            + (future.bounded_rationality_score * 0.10)
            + (causal_support * 0.25)
            + (consistency * 0.30),
            3,
        )

    def causal_support_score(
        self,
        future: CandidateFuture,
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation],
    ) -> float:
        hypotheses_by_id = {
            item.hypothesis_id: item for item in hypotheses
        }
        selected_ids = set(future.supporting_hypotheses).intersection(
            hypotheses_by_id
        )
        total_confidence = sum(
            item.confidence for item in hypotheses
        )
        weighted_support = sum(
            hypotheses_by_id[item].confidence for item in selected_ids
        )
        score = (
            weighted_support / total_confidence
            if total_confidence
            else 0.0
        )
        for relation in relations:
            source_selected = (
                relation.source_hypothesis_id in selected_ids
            )
            target_selected = (
                relation.target_hypothesis_id in selected_ids
            )
            if source_selected and target_selected:
                if relation.relation_type == "supports":
                    score += 0.12 * relation.strength
                elif relation.relation_type == "contradicts":
                    score -= 0.18 * relation.strength
                else:
                    score += 0.05 * relation.strength
            elif (
                relation.relation_type == "conditions"
                and target_selected
                and not source_selected
            ):
                score -= 0.08 * relation.strength
        return min(1.0, max(0.0, score))

    def select(
        self,
        futures: list[CandidateFuture],
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation] | None = None,
    ) -> CandidateFuture:
        return max(
            futures,
            key=lambda future: self.score(
                future,
                objective_state,
                subjective_models,
                hypotheses,
                relations,
            ),
        )
