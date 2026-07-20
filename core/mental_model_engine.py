from schemas import Belief, MentalModel, Observation, SubjectiveWorldModel


class MentalModelEngine:
    def build(
        self,
        observation: Observation,
        belief: Belief,
        model: SubjectiveWorldModel,
        mental_model_id: str,
    ) -> MentalModel:
        if "监控" in belief.proposition:
            assumptions = ["technical anomalies may be caused by institutional surveillance"]
        elif "安全升级" in belief.proposition:
            assumptions = ["technical anomalies may be side effects of a security upgrade"]
        else:
            assumptions = ["available evidence supports multiple institutional explanations"]

        institutional_weight = model.theory_of_change.institutions
        expectation = (
            "institutions strongly shape individual options"
            if institutional_weight >= 0.6
            else "institutional intent must be inferred from additional evidence"
        )
        return MentalModel(
            mental_model_id=mental_model_id,
            agent_id=model.agent_id,
            source_belief_ids=[belief.belief_id],
            source_observation_ids=[observation.observation_id],
            causal_assumptions=assumptions,
            institutional_expectation=expectation,
            relevant_value_weights={
                name: value.base_weight
                for name, value in model.values.items()
                if name in {"freedom", "safety", "order", "truth"}
            },
            uncertainty_tolerance=model.epistemology.tolerance_for_uncertainty,
        )
