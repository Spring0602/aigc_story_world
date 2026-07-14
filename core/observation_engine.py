from schemas import ObjectiveWorldState, Observation, SubjectiveWorldModel


class ObservationEngine:
    def observe(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
    ) -> list[Observation]:
        observations: list[Observation] = []
        for model in subjective_models:
            for item in objective_state.public_information:
                observations.append(
                    Observation(
                        observation_id=f"obs_{objective_state.step:03d}_{model.agent_id}_{item.info_id}",
                        agent_id=model.agent_id,
                        step=objective_state.step,
                        source=item.source,
                        content=item.content,
                        reliability=0.82,
                        visibility="public",
                    )
                )

            if model.agent_id == "lin_xia":
                observations.append(
                    Observation(
                        observation_id=f"obs_{objective_state.step:03d}_lin_xia_dns",
                        agent_id="lin_xia",
                        step=objective_state.step,
                        source="terminal",
                        content="部分 DNS 请求被重定向。",
                        reliability=0.92,
                        visibility="private",
                    )
                )
        return observations
