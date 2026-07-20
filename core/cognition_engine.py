from core.belief_updater import BeliefUpdater
from core.bias_filter import BiasFilter
from core.evidence_evaluator import EvidenceEvaluator
from core.interpretation_engine import InterpretationEngine
from core.mental_model_engine import MentalModelEngine
from schemas import BiasFilterResult, Interpretation, MentalModel, Observation, SubjectiveWorldModel


class CognitionEngine:
    def __init__(self) -> None:
        self.evidence_evaluator = EvidenceEvaluator()
        self.belief_updater = BeliefUpdater()
        self.mental_model_engine = MentalModelEngine()
        self.bias_filter = BiasFilter()
        self.interpretation_engine = InterpretationEngine()

    def interpret(
        self,
        observations: list[Observation],
        subjective_models: list[SubjectiveWorldModel],
    ) -> tuple[
        list[SubjectiveWorldModel],
        list[MentalModel],
        list[BiasFilterResult],
        list[Interpretation],
    ]:
        models_by_agent = {model.agent_id: model for model in subjective_models}
        mental_models: list[MentalModel] = []
        bias_results: list[BiasFilterResult] = []
        interpretations: list[Interpretation] = []

        for observation in observations:
            model = models_by_agent[observation.agent_id]
            confidence = self.evidence_evaluator.score(observation, model)
            updated_model = self.belief_updater.update(model, observation, confidence)
            models_by_agent[observation.agent_id] = updated_model

            sequence = len(interpretations) + 1
            cognitive_id = f"{observation.step:03d}_{sequence:03d}"
            belief = updated_model.beliefs[-1]
            mental_model = self.mental_model_engine.build(
                observation=observation,
                belief=belief,
                model=updated_model,
                mental_model_id=f"mm_{cognitive_id}",
            )
            bias_result = self.bias_filter.apply(
                mental_model=mental_model,
                model=updated_model,
                bias_filter_id=f"bias_{cognitive_id}",
            )
            mental_models.append(mental_model)
            bias_results.append(bias_result)
            interpretation = self.interpretation_engine.interpret(
                observation=observation,
                model=updated_model,
                belief=belief,
                mental_model=mental_model,
                bias_result=bias_result,
                confidence=confidence,
                interpretation_id=f"int_{cognitive_id}",
            )
            updated_model.emotion = interpretation.emotional_response.model_copy(deep=True)
            models_by_agent[observation.agent_id] = updated_model
            interpretations.append(interpretation)

        return list(models_by_agent.values()), mental_models, bias_results, interpretations
