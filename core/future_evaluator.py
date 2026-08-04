from typing import Any

from pydantic import BaseModel

from core.agent_consistency import AgentConsistency
from schemas import (
    AgentActionDecision,
    CandidateFuture,
    CausalHypothesis,
    FutureEvaluation,
    FutureScoreBreakdown,
    HypothesisRelation,
    ObjectiveWorldState,
    SubjectiveWorldModel,
)


class FutureEvaluator:
    def __init__(self) -> None:
        self.agent_consistency = AgentConsistency()

    def evaluate(
        self,
        future: CandidateFuture,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation] | None = None,
        action_decisions: list[AgentActionDecision] | None = None,
    ) -> FutureEvaluation:
        active_relations = relations or []
        active_decisions = self._source_decisions(
            future,
            action_decisions or [],
        )
        causal_support = self.causal_support_score(
            future,
            hypotheses,
            active_relations,
        )
        agent_consistency = self.agent_consistency.score(
            future,
            subjective_models,
            active_decisions,
        )
        constraint_satisfaction = self._constraint_score(active_decisions)
        state_compatibility = self._state_compatibility(
            future,
            objective_state,
        )
        epistemic_compatibility = future.belief_plausibility
        action_compatibility = (
            sum(
                item.score_breakdown.weighted_score
                for item in active_decisions
            )
            / len(active_decisions)
            if active_decisions
            else future.bounded_rationality_score
        )
        compatibility = self._clamp(
            state_compatibility * 0.50
            + epistemic_compatibility * 0.20
            + action_compatibility * 0.30
        )
        cross_lens_support = self._cross_lens_support(
            future,
            active_relations,
        )
        contradiction_penalty = self._contradiction_penalty(
            future,
            hypotheses,
            active_relations,
        )
        final_score = self._clamp(
            future.estimated_plausibility * 0.15
            + causal_support * 0.20
            + agent_consistency * 0.20
            + constraint_satisfaction * 0.15
            + compatibility * 0.20
            + cross_lens_support * 0.10
            - contradiction_penalty * 0.15
        )
        relevant_relations = self._relevant_relations(future, active_relations)
        constraint_ids = sorted(
            {
                constraint_id
                for decision in active_decisions
                for constraint_id in decision.constraint_ids
            }
        )
        breakdown = FutureScoreBreakdown(
            estimated_plausibility=round(future.estimated_plausibility, 3),
            causal_support=round(causal_support, 3),
            agent_consistency=round(agent_consistency, 3),
            constraint_satisfaction=round(constraint_satisfaction, 3),
            state_compatibility=round(state_compatibility, 3),
            epistemic_compatibility=round(epistemic_compatibility, 3),
            action_compatibility=round(action_compatibility, 3),
            compatibility=round(compatibility, 3),
            cross_lens_support=round(cross_lens_support, 3),
            contradiction_penalty=round(contradiction_penalty, 3),
            final_score=round(final_score, 3),
        )
        return FutureEvaluation(
            evaluation_id=f"future_evaluation_{future.future_id}",
            future_id=future.future_id,
            source_state_id=future.source_state_id,
            evaluated_state_id=objective_state.state_id,
            step=objective_state.step + 1,
            score_breakdown=breakdown,
            supporting_hypothesis_ids=list(future.supporting_hypotheses),
            opposing_hypothesis_ids=list(future.opposing_hypotheses),
            supporting_relation_ids=self._relation_ids(
                relevant_relations,
                "supports",
            ),
            contradicting_relation_ids=self._relation_ids(
                relevant_relations,
                "contradicts",
            ),
            conditioning_relation_ids=self._relation_ids(
                relevant_relations,
                "conditions",
            ),
            evaluated_constraint_ids=constraint_ids,
            state_change_paths=[
                change.path for change in future.expected_state_changes
            ],
            action_decision_ids=[
                decision.action_decision_id for decision in active_decisions
            ],
            rationale=(
                "Future score combines causal support, agent consistency, "
                "constraint satisfaction, state/belief/action compatibility, "
                "cross-lens reinforcement, and explicit contradiction cost."
            ),
        )

    def score(
        self,
        future: CandidateFuture,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation] | None = None,
        action_decisions: list[AgentActionDecision] | None = None,
    ) -> float:
        return self.evaluate(
            future,
            objective_state,
            subjective_models,
            hypotheses,
            relations,
            action_decisions,
        ).score_breakdown.final_score

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
        total_confidence = sum(item.confidence for item in hypotheses)
        weighted_support = sum(
            hypotheses_by_id[item].confidence for item in selected_ids
        )
        score = weighted_support / total_confidence if total_confidence else 0.0
        for relation in relations:
            source_selected = relation.source_hypothesis_id in selected_ids
            target_selected = relation.target_hypothesis_id in selected_ids
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
        return self._clamp(score)

    def select(
        self,
        futures: list[CandidateFuture],
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation] | None = None,
        action_decisions: list[AgentActionDecision] | None = None,
    ) -> CandidateFuture:
        return max(
            futures,
            key=lambda future: self.score(
                future,
                objective_state,
                subjective_models,
                hypotheses,
                relations,
                action_decisions,
            ),
        )

    def _source_decisions(
        self,
        future: CandidateFuture,
        action_decisions: list[AgentActionDecision],
    ) -> list[AgentActionDecision]:
        source_ids = set(future.source_action_decision_ids)
        return [
            item
            for item in action_decisions
            if item.action_decision_id in source_ids
        ]

    def _constraint_score(
        self,
        decisions: list[AgentActionDecision],
    ) -> float:
        if not decisions:
            return 0.5
        return sum(
            item.score_breakdown.constraint_satisfaction for item in decisions
        ) / len(decisions)

    def _state_compatibility(
        self,
        future: CandidateFuture,
        state: ObjectiveWorldState,
    ) -> float:
        source_score = (
            1.0
            if future.source_state_id == state.state_id
            else 0.5 if not future.source_state_id else 0.0
        )
        if not future.expected_state_changes:
            return (source_score + 0.5) / 2

        change_scores = []
        for change in future.expected_state_changes:
            found, current_value = self._read_path(state, change.path)
            score = 0.0
            if found:
                score += 0.35
                if current_value == change.old_value:
                    score += 0.45
                if current_value != change.new_value:
                    score += 0.20
            change_scores.append(score)
        return source_score * 0.20 + sum(change_scores) / len(change_scores) * 0.80

    def _read_path(
        self,
        state: ObjectiveWorldState,
        path: str,
    ) -> tuple[bool, Any]:
        current: Any = state
        for part in path.split("."):
            if isinstance(current, BaseModel):
                if not hasattr(current, part):
                    return False, None
                current = getattr(current, part)
            elif isinstance(current, dict):
                if part not in current:
                    return False, None
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if index >= len(current):
                    return False, None
                current = current[index]
            else:
                return False, None
        return True, current

    def _cross_lens_support(
        self,
        future: CandidateFuture,
        relations: list[HypothesisRelation],
    ) -> float:
        relevant = self._relevant_relations(future, relations)
        if not relevant:
            return 0.5
        values = []
        for relation in relevant:
            if relation.relation_type == "supports":
                values.append(relation.strength)
            elif relation.relation_type == "conditions":
                values.append(0.5 + relation.strength * 0.5)
            else:
                values.append(1.0 - relation.strength)
        return sum(values) / len(values)

    def _contradiction_penalty(
        self,
        future: CandidateFuture,
        hypotheses: list[CausalHypothesis],
        relations: list[HypothesisRelation],
    ) -> float:
        hypotheses_by_id = {
            item.hypothesis_id: item for item in hypotheses
        }
        penalties = [
            hypotheses_by_id[item].confidence
            for item in future.opposing_hypotheses
            if item in hypotheses_by_id
        ]
        penalties.extend(
            relation.strength
            for relation in self._relevant_relations(future, relations)
            if relation.relation_type == "contradicts"
        )
        return sum(penalties) / len(penalties) if penalties else 0.0

    def _relevant_relations(
        self,
        future: CandidateFuture,
        relations: list[HypothesisRelation],
    ) -> list[HypothesisRelation]:
        support_ids = set(future.supporting_hypotheses)
        opposing_ids = set(future.opposing_hypotheses)
        all_ids = support_ids | opposing_ids
        return [
            relation
            for relation in relations
            if relation.source_hypothesis_id in all_ids
            and relation.target_hypothesis_id in all_ids
            and (
                relation.source_hypothesis_id in support_ids
                or relation.target_hypothesis_id in support_ids
            )
        ]

    def _relation_ids(
        self,
        relations: list[HypothesisRelation],
        relation_type: str,
    ) -> list[str]:
        return [
            relation.relation_id
            for relation in relations
            if relation.relation_type == relation_type
        ]

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))
