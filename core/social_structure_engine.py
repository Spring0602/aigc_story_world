from schemas import (
    BeliefState,
    BiasFilterResult,
    CandidateFuture,
    InstitutionPowerAssessment,
    MentalModel,
    NormPressureAssessment,
    Observation,
    ObjectiveWorldState,
    PsychologyContext,
    RoleAssessment,
    SocialActionEvaluation,
    SocialContext,
    SubjectiveWorldModel,
)


class SocialStructureEngine:
    def assess_context(
        self,
        objective_state: ObjectiveWorldState,
        observations: list[Observation],
        subjective_models: list[SubjectiveWorldModel],
        belief_states: list[BeliefState],
    ) -> SocialContext:
        observations_by_agent: dict[str, list[Observation]] = {}
        for observation in observations:
            observations_by_agent.setdefault(observation.agent_id, []).append(
                observation
            )
        beliefs_by_agent = {item.agent_id: item for item in belief_states}

        role_assessments = []
        norm_pressures = []
        institution_powers = []
        for model in subjective_models:
            observations_for_agent = observations_by_agent.get(model.agent_id, [])
            observation_ids = [
                item.observation_id for item in observations_for_agent
            ]
            belief_state = beliefs_by_agent[model.agent_id]
            world_agent = objective_state.agents.get(model.agent_id)
            roles = sorted(
                set(model.roles)
                | set(world_agent.roles if world_agent is not None else [])
            )
            role_constraint = self._role_constraint(roles)
            freedom = self._value_weight(model, "freedom")
            order = self._value_weight(model, "order")
            role_conflict = self._clamp(
                role_constraint * ((freedom * 0.65) + ((1.0 - order) * 0.35))
            )
            role_assessments.append(
                RoleAssessment(
                    role_assessment_id=(
                        f"role_{objective_state.step:03d}_{model.agent_id}"
                    ),
                    agent_id=model.agent_id,
                    step=objective_state.step,
                    observation_ids=observation_ids,
                    belief_state_id=belief_state.belief_state_id,
                    roles=roles,
                    expected_behaviors=self._expected_behaviors(roles),
                    role_constraint=role_constraint,
                    role_conflict=role_conflict,
                )
            )

            for norm in objective_state.norms.values():
                sanction_severity = self._clamp(len(norm.sanctions) / 3.0)
                compliance_pressure = self._clamp(
                    (norm.clarity * 0.35)
                    + (sanction_severity * 0.4)
                    + (model.epistemology.trust_authority * 0.25)
                )
                norm_pressures.append(
                    NormPressureAssessment(
                        norm_pressure_id=(
                            f"norm_pressure_{objective_state.step:03d}_"
                            f"{model.agent_id}_{norm.norm_id}"
                        ),
                        agent_id=model.agent_id,
                        step=objective_state.step,
                        observation_ids=observation_ids,
                        belief_state_id=belief_state.belief_state_id,
                        norm_id=norm.norm_id,
                        institution_id=norm.institution_id,
                        clarity=norm.clarity,
                        sanction_severity=sanction_severity,
                        compliance_pressure=compliance_pressure,
                    )
                )

            for institution in objective_state.institutions.values():
                scope = min(1.0, len(institution.authority_scope) / 2.0)
                controlled = (
                    len(institution.resources_controlled)
                    / max(1, len(objective_state.resources))
                )
                resource_dependence = self._clamp(controlled)
                authority_power = self._clamp(
                    (scope * 0.3)
                    + (resource_dependence * 0.4)
                    + ((1.0 - institution.transparency) * 0.3)
                )
                subordinate_role = 1.0 if "student" in roles else 0.5
                power_asymmetry = self._clamp(
                    (authority_power * 0.8) + (subordinate_role * 0.2)
                )
                institution_powers.append(
                    InstitutionPowerAssessment(
                        institution_power_id=(
                            f"institution_power_{objective_state.step:03d}_"
                            f"{model.agent_id}_{institution.institution_id}"
                        ),
                        agent_id=model.agent_id,
                        step=objective_state.step,
                        observation_ids=observation_ids,
                        belief_state_id=belief_state.belief_state_id,
                        institution_id=institution.institution_id,
                        authority_scope=institution.authority_scope,
                        controlled_resource_ids=(
                            institution.resources_controlled
                        ),
                        transparency=institution.transparency,
                        resource_dependence=resource_dependence,
                        authority_power=authority_power,
                        power_asymmetry=power_asymmetry,
                    )
                )

        return SocialContext(
            role_assessments=role_assessments,
            norm_pressures=norm_pressures,
            institution_powers=institution_powers,
        )

    def evaluate_actions(
        self,
        context: SocialContext,
        objective_state: ObjectiveWorldState,
        candidate_futures: list[CandidateFuture],
        psychology: PsychologyContext,
        bias_results: list[BiasFilterResult],
        mental_models: list[MentalModel],
        step: int,
    ) -> SocialContext:
        roles = {item.agent_id: item for item in context.role_assessments}
        norms_by_agent: dict[str, list[NormPressureAssessment]] = {}
        for item in context.norm_pressures:
            norms_by_agent.setdefault(item.agent_id, []).append(item)
        powers_by_agent: dict[str, list[InstitutionPowerAssessment]] = {}
        for item in context.institution_powers:
            powers_by_agent.setdefault(item.agent_id, []).append(item)
        motivations = {
            item.agent_id: item for item in psychology.motivation_states
        }
        emotions = {
            item.agent_id: item for item in psychology.emotional_appraisals
        }
        mental_model_agents = {
            item.mental_model_id: item.agent_id for item in mental_models
        }
        biases_by_agent: dict[str, list[BiasFilterResult]] = {}
        for item in bias_results:
            agent_id = mental_model_agents.get(item.mental_model_id)
            if agent_id is not None:
                biases_by_agent.setdefault(agent_id, []).append(item)

        actions = sorted(
            {
                (item.agent_id, item.action)
                for future in candidate_futures
                for item in future.agent_actions
            }
        )
        evaluations = []
        for sequence, (agent_id, action) in enumerate(actions, start=1):
            role = roles[agent_id]
            norms = norms_by_agent.get(agent_id, [])
            powers = powers_by_agent.get(agent_id, [])
            motivation = motivations.get(agent_id)
            emotion = emotions.get(agent_id)
            biases = biases_by_agent.get(agent_id, [])
            pressure = self._average(
                [item.compliance_pressure for item in norms],
                default=0.0,
            )
            power = self._average(
                [item.power_asymmetry for item in powers],
                default=0.0,
            )
            role_alignment, norm_compliance, risk_factor = (
                self._action_social_profile(action)
            )
            institutional_risk = self._clamp(
                power * risk_factor * (0.7 + (pressure * 0.3))
            )
            social_support = self._social_support(
                objective_state,
                agent_id,
                action,
            )
            compatibility = self._clamp(
                (role_alignment * 0.25)
                + (norm_compliance * 0.25)
                + ((1.0 - institutional_risk) * 0.3)
                + (social_support * 0.2)
            )
            if motivation and action == motivation.preferred_action:
                compatibility = self._clamp(
                    compatibility + (motivation.intensity * 0.05)
                )
            evaluations.append(
                SocialActionEvaluation(
                    social_evaluation_id=(
                        f"social_evaluation_{step:03d}_{sequence:03d}"
                    ),
                    agent_id=agent_id,
                    step=step,
                    action=action,
                    belief_state_id=role.belief_state_id,
                    role_assessment_id=role.role_assessment_id,
                    norm_pressure_ids=[
                        item.norm_pressure_id for item in norms
                    ],
                    institution_power_ids=[
                        item.institution_power_id for item in powers
                    ],
                    motivation_state_id=(
                        motivation.motivation_state_id
                        if motivation is not None
                        else None
                    ),
                    emotional_appraisal_id=(
                        emotion.emotional_appraisal_id
                        if emotion is not None
                        else None
                    ),
                    bias_filter_ids=[
                        item.bias_filter_id for item in biases
                    ],
                    role_alignment=role_alignment,
                    norm_compliance=norm_compliance,
                    institutional_risk=institutional_risk,
                    social_support=social_support,
                    compatibility=compatibility,
                    rationale=(
                        f"role-alignment={role_alignment:.3f}; "
                        f"norm-compliance={norm_compliance:.3f}; "
                        f"institutional-risk={institutional_risk:.3f}; "
                        f"social-support={social_support:.3f}."
                    ),
                )
            )

        return context.model_copy(
            update={"action_evaluations": evaluations},
            deep=True,
        )

    def _role_constraint(self, roles: list[str]) -> float:
        constraints = {
            "student": 0.72,
            "roommate": 0.28,
            "staff": 0.45,
            "administrator": 0.2,
        }
        return max(
            (constraints.get(role, 0.4) for role in roles),
            default=0.4,
        )

    def _expected_behaviors(self, roles: list[str]) -> list[str]:
        expectations = {
            "student": "comply_with_campus_policy",
            "roommate": "maintain_peer_solidarity",
            "staff": "follow_institutional_procedure",
            "administrator": "enforce_institutional_rules",
        }
        return sorted(
            {
                expectations[role]
                for role in roles
                if role in expectations
            }
        )

    def _action_social_profile(
        self,
        action: str,
    ) -> tuple[float, float, float]:
        if "confront" in action:
            return 0.3, 0.15, 1.0
        if "secretly" in action:
            return 0.62, 0.42, 0.5
        if "help" in action:
            return 0.82, 0.7, 0.28
        if "delay" in action:
            return 0.95, 0.95, 0.08
        return 0.5, 0.5, 0.5

    def _social_support(
        self,
        objective_state: ObjectiveWorldState,
        agent_id: str,
        action: str,
    ) -> float:
        relationships = [
            item
            for item in objective_state.relationships.values()
            if agent_id in {item.source, item.target}
        ]
        trust = self._average(
            [item.trust for item in relationships],
            default=0.5,
        )
        if "help" in action:
            return self._clamp(trust + 0.15)
        if "confront" in action:
            return self._clamp(trust * 0.55)
        return trust

    def _value_weight(
        self,
        model: SubjectiveWorldModel,
        name: str,
    ) -> float:
        value = model.values.get(name)
        return value.base_weight if value is not None else 0.5

    def _average(self, values: list[float], default: float) -> float:
        return sum(values) / len(values) if values else default

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))
