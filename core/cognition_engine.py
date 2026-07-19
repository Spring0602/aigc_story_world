from core.belief_updater import BeliefUpdater
from core.evidence_evaluator import EvidenceEvaluator
from schemas import Interpretation, Observation, SubjectiveWorldModel


class CognitionEngine:
    def __init__(self) -> None:
        self.evidence_evaluator = EvidenceEvaluator()
        self.belief_updater = BeliefUpdater()

    def interpret(
        self,
        observations: list[Observation],
        subjective_models: list[SubjectiveWorldModel],
    ) -> tuple[list[SubjectiveWorldModel], list[Interpretation]]:
        models_by_agent = {model.agent_id: model for model in subjective_models}
        interpretations: list[Interpretation] = []

        for observation in observations:
            model = models_by_agent[observation.agent_id]
            confidence = self.evidence_evaluator.score(observation, model)
            updated_model = self.belief_updater.update(model, observation, confidence)
            models_by_agent[observation.agent_id] = updated_model

            claim = updated_model.beliefs[-1].proposition
            basis = [self.evidence_evaluator.trust_basis(observation)]
            interpretations.append(
                Interpretation(
                    interpretation_id=f"int_{len(interpretations) + 1:03d}",
                    agent_id=observation.agent_id,
                    observation_ids=[observation.observation_id],
                    claim=claim,
                    confidence=confidence,
                    reasoning_basis=basis,
                )
            )

        return list(models_by_agent.values()), interpretations
