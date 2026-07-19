from core.belief_updater import BeliefUpdater
from core.evidence_evaluator import EvidenceEvaluator
from core.interpretation_engine import InterpretationEngine
from schemas import Interpretation, Observation, SubjectiveWorldModel


class CognitionEngine:
    def __init__(self) -> None:
        self.evidence_evaluator = EvidenceEvaluator()
        self.belief_updater = BeliefUpdater()
        self.interpretation_engine = InterpretationEngine()

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

            interpretation = self.interpretation_engine.interpret(
                observation=observation,
                model=updated_model,
                belief=updated_model.beliefs[-1],
                confidence=confidence,
                interpretation_id=f"int_{len(interpretations) + 1:03d}",
            )
            updated_model.emotion = interpretation.emotional_response.model_copy(deep=True)
            models_by_agent[observation.agent_id] = updated_model
            interpretations.append(interpretation)

        return list(models_by_agent.values()), interpretations
