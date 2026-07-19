from schemas import InformationItem, ObjectiveWorldState, Observation, SubjectiveWorldModel


class ObservationEngine:
    def observe(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[Observation]:
        observations: list[Observation] = []
        for model in subjective_models:
            agent = objective_state.agents.get(model.agent_id)
            if agent is None:
                continue

            for item in [*objective_state.public_information, *objective_state.hidden_facts]:
                if not self._is_visible(item, agent.location_id, agent.roles, model.agent_id):
                    continue
                observations.append(
                    Observation(
                        observation_id=f"obs_{objective_state.step:03d}_{model.agent_id}_{item.info_id}",
                        information_id=item.info_id,
                        agent_id=model.agent_id,
                        step=objective_state.step,
                        source=item.source,
                        evidence_type=item.evidence_type,
                        content=item.content,
                        reliability=item.reliability,
                        visibility=item.visibility,
                        location_id=item.location_id,
                        provenance=item.provenance,
                    )
                )
        return observations

    def _is_visible(
        self,
        item: InformationItem,
        agent_location_id: str,
        agent_roles: list[str],
        agent_id: str,
    ) -> bool:
        if item.visibility == "hidden":
            return False
        if item.location_id is not None and item.location_id != agent_location_id:
            return False
        if item.visibility == "public":
            return True
        if item.visibility == "private":
            return agent_id in item.allowed_agent_ids
        return bool(set(agent_roles).intersection(item.allowed_roles))
