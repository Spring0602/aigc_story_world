from schemas import Observation, SubjectiveWorldModel


class EvidenceEvaluator:
    TRUST_FIELD_BY_EVIDENCE = {
        "data": "trust_data",
        "authority": "trust_authority",
        "personal_experience": "trust_personal_experience",
        "social_consensus": "trust_social_consensus",
        "intuition": "trust_intuition",
    }

    def score(self, observation: Observation, model: SubjectiveWorldModel) -> float:
        source_weight = getattr(model.epistemology, self.trust_basis(observation))
        return min(1.0, max(0.0, (observation.reliability * 0.65) + (source_weight * 0.35)))

    def trust_basis(self, observation: Observation) -> str:
        return self.TRUST_FIELD_BY_EVIDENCE[observation.evidence_type]
