from schemas import Observation, SubjectiveWorldModel


class EvidenceEvaluator:
    def score(self, observation: Observation, model: SubjectiveWorldModel) -> float:
        trust_data = model.epistemology.get("trust_data", 0.5)
        trust_authority = model.epistemology.get("trust_authority", 0.5)
        source_weight = trust_data if observation.source == "terminal" else trust_authority
        return min(1.0, max(0.0, (observation.reliability * 0.65) + (source_weight * 0.35)))
