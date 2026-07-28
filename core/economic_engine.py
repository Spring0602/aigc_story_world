from schemas import (
    BeliefState,
    CandidateFuture,
    EconomicActionEvaluation,
    EconomicContext,
    IncentiveAssessment,
    InformationAsymmetryAssessment,
    InformationBoundary,
    MotivationState,
    ObjectiveWorldState,
    Observation,
    OpportunityCostAssessment,
    ScarcityAssessment,
    SubjectiveWorldModel,
)


class EconomicEngine:
    def assess_context(
        self,
        objective_state: ObjectiveWorldState,
        subjective_models: list[SubjectiveWorldModel],
        observations: list[Observation] | None = None,
        belief_states: list[BeliefState] | None = None,
    ) -> EconomicContext:
        observations = observations or []
        belief_states = belief_states or [
            self._fallback_belief_state(model, objective_state.step)
            for model in subjective_models
        ]
        observations_by_agent: dict[str, list[Observation]] = {}
        for observation in observations:
            observations_by_agent.setdefault(observation.agent_id, []).append(
                observation
            )
        beliefs_by_agent = {item.agent_id: item for item in belief_states}
        all_information_ids = {
            item.info_id
            for item in [
                *objective_state.public_information,
                *objective_state.hidden_facts,
            ]
        }
        information_boundaries = []
        for model in subjective_models:
            agent_observations = observations_by_agent.get(model.agent_id, [])
            visible_information_ids = sorted(
                {item.information_id for item in agent_observations}
            )
            inaccessible_information_ids = sorted(
                all_information_ids - set(visible_information_ids)
            )
            coverage = (
                len(visible_information_ids) / len(all_information_ids)
                if all_information_ids
                else 1.0
            )
            information_boundaries.append(
                InformationBoundary(
                    information_boundary_id=(
                        f"information_boundary_{objective_state.step:03d}_"
                        f"{model.agent_id}"
                    ),
                    agent_id=model.agent_id,
                    step=objective_state.step,
                    source_world_step=objective_state.step,
                    observation_ids=[
                        item.observation_id for item in agent_observations
                    ],
                    visible_information_ids=visible_information_ids,
                    inaccessible_information_ids=inaccessible_information_ids,
                    visible_resource_ids=sorted(objective_state.resources),
                    access_rule_ids=sorted(
                        {
                            rule
                            for resource in objective_state.resources.values()
                            for rule in resource.access_rules
                        }
                    ),
                    coverage=coverage,
                )
            )
        boundaries_by_agent = {
            item.agent_id: item for item in information_boundaries
        }

        demand = max(1, len(subjective_models))
        scarcity_assessments = []
        for model in subjective_models:
            boundary = boundaries_by_agent[model.agent_id]
            belief_state = beliefs_by_agent[model.agent_id]
            for resource in objective_state.resources.values():
                publicly_accessible = (
                    resource.owner_id is None and not resource.access_rules
                )
                access_level = (
                    1.0
                    if publicly_accessible or resource.owner_id == model.agent_id
                    else 0.55
                )
                if resource.access_rules:
                    access_level -= 0.2
                access_level = self._clamp(access_level)
                physical_scarcity = 1.0 - min(1.0, resource.quantity / demand)
                access_scarcity = 1.0 - access_level
                scarcity_level = self._clamp(
                    (physical_scarcity * 0.4)
                    + (access_scarcity * 0.5)
                    + (belief_state.uncertainty * 0.1)
                )
                scarcity_assessments.append(
                    ScarcityAssessment(
                        scarcity_assessment_id=(
                            f"scarcity_{objective_state.step:03d}_"
                            f"{model.agent_id}_{resource.resource_id}"
                        ),
                        agent_id=model.agent_id,
                        step=objective_state.step,
                        information_boundary_id=boundary.information_boundary_id,
                        belief_state_id=belief_state.belief_state_id,
                        resource_id=resource.resource_id,
                        available_quantity=resource.quantity,
                        access_level=access_level,
                        physical_scarcity=physical_scarcity,
                        access_scarcity=access_scarcity,
                        scarcity_level=scarcity_level,
                        constraint_ids=resource.access_rules,
                    )
                )

        transparency = (
            sum(item.transparency for item in objective_state.institutions.values())
            / len(objective_state.institutions)
            if objective_state.institutions
            else 1.0
        )
        informed_parties = sorted(objective_state.institutions)
        information_asymmetries = []
        for model in subjective_models:
            boundary = boundaries_by_agent[model.agent_id]
            belief_state = beliefs_by_agent[model.agent_id]
            boundary_opacity = 1.0 - boundary.coverage
            asymmetry_level = self._clamp(
                ((1.0 - transparency) * 0.5)
                + (boundary_opacity * 0.35)
                + (belief_state.uncertainty * 0.15)
            )
            information_asymmetries.append(
                InformationAsymmetryAssessment(
                    information_asymmetry_id=(
                        f"information_asymmetry_{objective_state.step:03d}_"
                        f"{model.agent_id}"
                    ),
                    agent_id=model.agent_id,
                    step=objective_state.step,
                    information_boundary_id=boundary.information_boundary_id,
                    belief_state_id=belief_state.belief_state_id,
                    informed_party_ids=informed_parties,
                    visible_information_ids=boundary.visible_information_ids,
                    hidden_information_ids=boundary.inaccessible_information_ids,
                    institution_transparency=transparency,
                    asymmetry_level=asymmetry_level,
                )
            )
        return EconomicContext(
            information_boundaries=information_boundaries,
            scarcity_assessments=scarcity_assessments,
            information_asymmetries=information_asymmetries,
        )

    def evaluate_actions(
        self,
        context: EconomicContext,
        candidate_futures: list[CandidateFuture],
        subjective_models: list[SubjectiveWorldModel],
        step: int,
        motivation_states: list[MotivationState] | None = None,
    ) -> EconomicContext:
        models = {model.agent_id: model for model in subjective_models}
        motivations = {
            item.agent_id: item for item in (motivation_states or [])
        }
        boundaries = {
            item.agent_id: item for item in context.information_boundaries
        }
        scarcity_by_agent: dict[str, ScarcityAssessment] = {}
        for item in context.scarcity_assessments:
            current = scarcity_by_agent.get(item.agent_id)
            if current is None or item.scarcity_level > current.scarcity_level:
                scarcity_by_agent[item.agent_id] = item
        asymmetry_by_agent = {
            item.agent_id: item for item in context.information_asymmetries
        }
        actions_by_agent: dict[str, set[str]] = {}
        for future in candidate_futures:
            for proposed_action in future.agent_actions:
                actions_by_agent.setdefault(proposed_action.agent_id, set()).add(
                    proposed_action.action
                )

        incentives = []
        incentives_by_agent: dict[str, list[IncentiveAssessment]] = {}
        sequence = 0
        for agent_id, actions in sorted(actions_by_agent.items()):
            model = models[agent_id]
            boundary = boundaries[agent_id]
            scarcity = scarcity_by_agent[agent_id]
            asymmetry = asymmetry_by_agent[agent_id]
            motivation = motivations.get(agent_id)
            for action in sorted(actions):
                sequence += 1
                incentive = self._assess_incentive(
                    model,
                    action,
                    scarcity,
                    asymmetry,
                    boundary,
                    motivation,
                    incentive_id=f"incentive_{step:03d}_{sequence:03d}",
                    step=step,
                )
                incentives.append(incentive)
                incentives_by_agent.setdefault(agent_id, []).append(incentive)

        opportunity_costs = []
        evaluations = []
        evaluation_sequence = 0
        for agent_id, agent_incentives in sorted(incentives_by_agent.items()):
            scarcity = scarcity_by_agent[agent_id]
            asymmetry = asymmetry_by_agent[agent_id]
            for incentive in agent_incentives:
                evaluation_sequence += 1
                alternatives = [
                    item
                    for item in agent_incentives
                    if item.action != incentive.action
                ]
                forgone = max(
                    alternatives,
                    key=lambda item: item.net_incentive,
                    default=incentive,
                )
                opportunity_cost = self._clamp(
                    forgone.net_incentive - incentive.net_incentive
                )
                opportunity = OpportunityCostAssessment(
                    opportunity_cost_id=(
                        f"opportunity_cost_{step:03d}_{evaluation_sequence:03d}"
                    ),
                    agent_id=agent_id,
                    step=step,
                    action=incentive.action,
                    forgone_action=forgone.action,
                    forgone_net_incentive=forgone.net_incentive,
                    opportunity_cost=opportunity_cost,
                )
                opportunity_costs.append(opportunity)
                normalized_incentive = self._clamp(
                    (incentive.net_incentive + 1.0) / 2.0
                )
                utility = self._clamp(
                    normalized_incentive * (1.0 - (opportunity_cost * 0.4))
                )
                evaluations.append(
                    EconomicActionEvaluation(
                        economic_evaluation_id=(
                            f"economic_evaluation_{step:03d}_{evaluation_sequence:03d}"
                        ),
                        agent_id=agent_id,
                        step=step,
                        action=incentive.action,
                        information_boundary_id=(
                            incentive.information_boundary_id
                        ),
                        belief_state_id=incentive.belief_state_id,
                        motivation_state_id=incentive.motivation_state_id,
                        scarcity_assessment_id=scarcity.scarcity_assessment_id,
                        information_asymmetry_id=asymmetry.information_asymmetry_id,
                        incentive_assessment_id=incentive.incentive_assessment_id,
                        opportunity_cost_id=opportunity.opportunity_cost_id,
                        utility=utility,
                        rationale=(
                            f"net-incentive={incentive.net_incentive:.3f}; "
                            f"opportunity-cost={opportunity_cost:.3f}; "
                            f"scarcity={scarcity.scarcity_level:.3f}; "
                            f"information-asymmetry={asymmetry.asymmetry_level:.3f}."
                        ),
                    )
                )

        return context.model_copy(
            update={
                "incentive_assessments": incentives,
                "opportunity_costs": opportunity_costs,
                "action_evaluations": evaluations,
            },
            deep=True,
        )

    def _assess_incentive(
        self,
        model: SubjectiveWorldModel,
        action: str,
        scarcity: ScarcityAssessment,
        asymmetry: InformationAsymmetryAssessment,
        boundary: InformationBoundary,
        motivation: MotivationState | None,
        incentive_id: str,
        step: int,
    ) -> IncentiveAssessment:
        truth = self._value_weight(model, "truth")
        freedom = self._value_weight(model, "freedom")
        safety = self._value_weight(model, "safety")
        order = self._value_weight(model, "order")

        if "secretly" in action:
            benefits = {
                "evidence_gain": (truth + model.epistemology.trust_data) / 2.0,
                "autonomy_preservation": freedom,
            }
            costs = {
                "access_barrier": scarcity.scarcity_level * 0.55,
                "detection_risk": asymmetry.asymmetry_level * 0.25,
            }
        elif "confront" in action:
            benefits = {
                "accountability": (truth * 0.7) + (freedom * 0.3),
            }
            costs = {
                "sanction_exposure": 0.45 + (safety * 0.25),
                "information_disadvantage": asymmetry.asymmetry_level * 0.5,
            }
        elif "help" in action:
            benefits = {
                "risk_sharing": (truth + safety) / 2.0,
                "additional_information": 1.0 - (asymmetry.asymmetry_level * 0.4),
            }
            costs = {
                "coordination_cost": 0.25,
                "social_exposure": asymmetry.asymmetry_level * 0.2,
            }
        else:
            benefits = {
                "stability": (safety + order) / 2.0,
            }
            costs = {
                "lost_verification_window": ((truth + freedom) / 2.0) * 0.55,
                "continued_information_disadvantage": (
                    asymmetry.asymmetry_level * 0.25
                ),
            }

        expected_benefit = self._average(benefits)
        if motivation and action == motivation.preferred_action:
            expected_benefit = self._clamp(
                expected_benefit + (motivation.intensity * 0.1)
            )
        expected_cost = self._average(costs)
        return IncentiveAssessment(
            incentive_assessment_id=incentive_id,
            agent_id=model.agent_id,
            step=step,
            information_boundary_id=boundary.information_boundary_id,
            belief_state_id=scarcity.belief_state_id,
            motivation_state_id=(
                motivation.motivation_state_id if motivation else None
            ),
            action=action,
            benefits=benefits,
            costs=costs,
            expected_benefit=expected_benefit,
            expected_cost=expected_cost,
            net_incentive=max(
                -1.0,
                min(1.0, expected_benefit - expected_cost),
            ),
        )

    def _average(self, values: dict[str, float]) -> float:
        return sum(values.values()) / len(values) if values else 0.0

    def _fallback_belief_state(
        self,
        model: SubjectiveWorldModel,
        step: int,
    ) -> BeliefState:
        beliefs = [*model.beliefs, *model.false_beliefs]
        dominant = max(
            beliefs,
            key=lambda item: item.confidence,
            default=None,
        )
        return BeliefState(
            belief_state_id=f"belief_state_{step:03d}_{model.agent_id}_economic",
            agent_id=model.agent_id,
            step=step,
            belief_ids=[item.belief_id for item in beliefs],
            dominant_belief_id=dominant.belief_id if dominant else "",
            source_update_id="economic_context_fallback",
            uncertainty=1.0 - dominant.confidence if dominant else 0.5,
        )

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _clamp(self, value: float) -> float:
        return min(1.0, max(0.0, value))
