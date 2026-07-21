from schemas import BayesianBeliefUpdate, Belief, BeliefState, Evidence, SubjectiveWorldModel


class BeliefUpdater:
    def update(
        self,
        model: SubjectiveWorldModel,
        evidence: Evidence,
        update_id: str,
        belief_state_id: str,
        proposition: str | None = None,
    ) -> tuple[SubjectiveWorldModel, Belief, BayesianBeliefUpdate, BeliefState]:
        updated = model.model_copy(deep=True)
        proposition = proposition or self._proposition_for(model, evidence)
        existing = next((item for item in updated.beliefs if item.proposition == proposition), None)
        prior = existing.confidence if existing else 0.5
        likelihood_true, likelihood_false = self._likelihoods(evidence)
        posterior = self._posterior(prior, likelihood_true, likelihood_false)

        belief_id = existing.belief_id if existing else f"belief_{model.agent_id}_{len(updated.beliefs) + 1:03d}"
        belief_update = BayesianBeliefUpdate(
            update_id=update_id,
            agent_id=model.agent_id,
            belief_id=belief_id,
            evidence_id=evidence.evidence_id,
            prior=prior,
            likelihood_e_given_true=likelihood_true,
            likelihood_e_given_false=likelihood_false,
            posterior=posterior,
            polarity=evidence.polarity,
        )

        if existing is None:
            belief = Belief(
                belief_id=belief_id,
                proposition=proposition,
                confidence=posterior,
                evidence=[evidence.observation_id],
                source=evidence.source,
                last_updated_step=evidence.step,
                update_ids=[update_id],
            )
            updated.beliefs.append(belief)
        else:
            existing.confidence = posterior
            if evidence.observation_id not in existing.evidence:
                existing.evidence.append(evidence.observation_id)
            existing.source = evidence.source
            existing.last_updated_step = evidence.step
            existing.update_ids.append(update_id)
            belief = existing

        updated.memory.append(evidence.content)
        all_beliefs = [*updated.beliefs, *updated.false_beliefs]
        dominant = max(all_beliefs, key=lambda item: item.confidence)
        belief_state = BeliefState(
            belief_state_id=belief_state_id,
            agent_id=model.agent_id,
            step=evidence.step,
            belief_ids=[item.belief_id for item in all_beliefs],
            dominant_belief_id=dominant.belief_id,
            source_update_id=update_id,
            uncertainty=1.0 - dominant.confidence,
        )
        return updated, belief, belief_update, belief_state

    def _proposition_for(self, model: SubjectiveWorldModel, evidence: Evidence) -> str:
        freedom = model.values.get("freedom")
        freedom_weight = freedom.base_weight if freedom else 0.5
        trusts_direct_evidence = (
            evidence.evidence_type in {"data", "personal_experience"}
            and evidence.trust_weight >= 0.7
        )
        if trusts_direct_evidence and freedom_weight >= 0.7:
            return "学校可能正在监控学生网络。"
        if model.epistemology.trust_authority >= 0.7:
            return "网络异常更可能是安全升级带来的正常现象。"
        return "校园网升级存在尚未解释的异常。"

    def _likelihoods(self, evidence: Evidence) -> tuple[float, float]:
        support_likelihood = 0.5 + (0.49 * evidence.strength)
        contradiction_likelihood = 0.5 - (0.49 * evidence.strength)
        if evidence.polarity == "supports":
            return support_likelihood, contradiction_likelihood
        return contradiction_likelihood, support_likelihood

    def _posterior(self, prior: float, likelihood_true: float, likelihood_false: float) -> float:
        numerator = likelihood_true * prior
        denominator = numerator + (likelihood_false * (1.0 - prior))
        return numerator / denominator if denominator else prior
