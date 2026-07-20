from schemas import Belief, Observation, SubjectiveWorldModel


class BeliefUpdater:
    def update(
        self,
        model: SubjectiveWorldModel,
        observation: Observation,
        confidence: float,
    ) -> SubjectiveWorldModel:
        updated = model.model_copy(deep=True)
        freedom = model.values.get("freedom")
        freedom_weight = freedom.base_weight if freedom else 0.5
        direct_evidence_trust = {
            "data": model.epistemology.trust_data,
            "personal_experience": model.epistemology.trust_personal_experience,
        }.get(observation.evidence_type, 0.0)
        trusts_direct_evidence = direct_evidence_trust >= 0.7

        if trusts_direct_evidence and freedom_weight >= 0.7:
            proposition = "学校可能正在监控学生网络。"
        elif model.epistemology.trust_authority >= 0.7:
            proposition = "网络异常更可能是安全升级带来的正常现象。"
        else:
            proposition = "校园网升级存在尚未解释的异常。"

        updated.beliefs.append(
            Belief(
                belief_id=f"belief_{model.agent_id}_{len(updated.beliefs) + 1:03d}",
                proposition=proposition,
                confidence=confidence,
                evidence=[observation.observation_id],
                source=observation.source,
                last_updated_step=observation.step,
            )
        )
        updated.memory.append(observation.content)
        return updated
