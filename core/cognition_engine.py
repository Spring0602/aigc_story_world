from dataclasses import dataclass

from core.belief_updater import BeliefUpdater
from core.bias_filter import BiasFilter
from core.evidence_evaluator import EvidenceEvaluator
from core.interpretation_engine import InterpretationEngine
from core.mental_model_engine import MentalModelEngine
from schemas import (
    BayesianBeliefUpdate,
    BeliefState,
    BiasFilterResult,
    Evidence,
    Interpretation,
    MentalModel,
    Observation,
    SubjectiveWorldModel,
)


@dataclass
class CognitionResult:
    subjective_models: list[SubjectiveWorldModel]
    evidence: list[Evidence]
    belief_updates: list[BayesianBeliefUpdate]
    belief_states: list[BeliefState]
    mental_models: list[MentalModel]
    bias_results: list[BiasFilterResult]
    interpretations: list[Interpretation]


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
    ) -> CognitionResult:
        models_by_agent = {model.agent_id: model for model in subjective_models}
        evidence_records: list[Evidence] = []
        belief_updates: list[BayesianBeliefUpdate] = []
        belief_states: list[BeliefState] = []
        mental_models: list[MentalModel] = []
        bias_results: list[BiasFilterResult] = []
        interpretations: list[Interpretation] = []

        for sequence, observation in enumerate(observations, start=1):
            model = models_by_agent[observation.agent_id]
            cognitive_id = f"{observation.step:03d}_{sequence:03d}"
            evidence = self.evidence_evaluator.assess(
                observation,
                model,
                evidence_id=f"evidence_{cognitive_id}",
            )
            updated_model, belief, belief_update, belief_state = self.belief_updater.update(
                model,
                evidence,
                update_id=f"update_{cognitive_id}",
                belief_state_id=f"belief_state_{cognitive_id}",
            )
            models_by_agent[observation.agent_id] = updated_model

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
            interpretation = self.interpretation_engine.interpret(
                observation=observation,
                model=updated_model,
                belief=belief,
                mental_model=mental_model,
                bias_result=bias_result,
                confidence=belief.confidence,
                interpretation_id=f"int_{cognitive_id}",
            )
            updated_model.emotion = interpretation.emotional_response.model_copy(deep=True)
            models_by_agent[observation.agent_id] = updated_model
            evidence_records.append(evidence)
            belief_updates.append(belief_update)
            belief_states.append(belief_state)
            mental_models.append(mental_model)
            bias_results.append(bias_result)
            interpretations.append(interpretation)

        return CognitionResult(
            subjective_models=list(models_by_agent.values()),
            evidence=evidence_records,
            belief_updates=belief_updates,
            belief_states=belief_states,
            mental_models=mental_models,
            bias_results=bias_results,
            interpretations=interpretations,
        )
