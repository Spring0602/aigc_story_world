from schemas import Evidence, Observation, SubjectiveWorldModel


class EvidenceEvaluator:
    TRUST_FIELD_BY_EVIDENCE = {
        "data": "trust_data",
        "authority": "trust_authority",
        "personal_experience": "trust_personal_experience",
        "social_consensus": "trust_social_consensus",
        "intuition": "trust_intuition",
    }

    def score(self, observation: Observation, model: SubjectiveWorldModel) -> float:
        source_weight = self.trust_weight(observation, model)
        return min(1.0, max(0.0, (observation.reliability * 0.65) + (source_weight * 0.35)))

    def assess(
        self,
        observation: Observation,
        model: SubjectiveWorldModel,
        evidence_id: str,
    ) -> Evidence:
        trust_basis = self.trust_basis(observation)
        return Evidence(
            evidence_id=evidence_id,
            observation_id=observation.observation_id,
            agent_id=observation.agent_id,
            step=observation.step,
            source=observation.source,
            evidence_type=observation.evidence_type,
            content=observation.content,
            reliability=observation.reliability,
            trust_basis=trust_basis,
            trust_weight=getattr(model.epistemology, trust_basis),
            strength=self.score(observation, model),
            provenance=observation.provenance,
        )

    def trust_basis(self, observation: Observation) -> str:
        return self.TRUST_FIELD_BY_EVIDENCE[observation.evidence_type]

    def trust_weight(self, observation: Observation, model: SubjectiveWorldModel) -> float:
        return getattr(model.epistemology, self.trust_basis(observation))
