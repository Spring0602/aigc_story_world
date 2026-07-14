from core.agent_consistency import AgentConsistency
from schemas import CandidateFuture, CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class FutureEvaluator:
    def __init__(self) -> None:
        self.agent_consistency = AgentConsistency()

    def score(
        self,
        future: CandidateFuture,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
    ) -> float:
        causal_support = len(future.supporting_hypotheses) / max(1, len(hypotheses))
        consistency = self.agent_consistency.score(future, subjective_models)
        return round((future.estimated_plausibility * 0.45) + (causal_support * 0.25) + (consistency * 0.30), 3)

    def select(
        self,
        futures: list[CandidateFuture],
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        hypotheses: list[CausalHypothesis],
    ) -> CandidateFuture:
        return max(futures, key=lambda future: self.score(future, objective_state, subjective_models, hypotheses))
