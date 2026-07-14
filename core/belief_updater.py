from schemas import Belief, Observation, SubjectiveWorldModel


class BeliefUpdater:
    def update(
        self,
        model: SubjectiveWorldModel,
        observation: Observation,
        confidence: float,
    ) -> SubjectiveWorldModel:
        updated = model.model_copy(deep=True)
        if observation.source == "terminal" and model.agent_id == "lin_xia":
            proposition = "学校可能正在监控学生网络。"
        elif model.epistemology.get("trust_authority", 0.5) >= 0.7:
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
