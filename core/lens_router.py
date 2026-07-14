from lenses.economics import EconomicLens
from lenses.psychology import PsychologyLens
from lenses.social_structure import SocialStructureLens
from schemas import CausalHypothesis, ObjectiveWorldState, SubjectiveWorldModel


class LensRouter:
    def __init__(self) -> None:
        self.lenses = [PsychologyLens(), EconomicLens(), SocialStructureLens()]

    def analyze(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[CausalHypothesis]:
        hypotheses: list[CausalHypothesis] = []
        for lens in self.lenses:
            hypotheses.extend(lens.analyze(objective_state, subjective_models))
        return hypotheses
