from math import log

from schemas import (
    BayesianWorldRevision,
    BeliefDistribution,
    Evidence,
    InformationBoundary,
    Observation,
    PossibleWorld,
    PossibleWorldBelief,
    PossibleWorldContext,
    SubjectiveWorldModel,
    WorldEvidenceAssessment,
)


class PossibleWorldEngine:
    WORLD_TEMPLATES = (
        (
            "institutional_monitoring",
            "学校以安全系统为名实施了面向学生行为的制度性监控。",
            ["网络异常由制度安排造成", "数据处理范围超过普通运维"],
        ),
        (
            "protective_security",
            "学校部署的是防御性安全措施，并未以学生行为监控为目标。",
            ["异常检测用于网络防护", "制度声明基本可信"],
        ),
        (
            "technical_anomaly",
            "当前异常主要来自尚未定位的技术故障，制度意图仍不确定。",
            ["技术异常可以独立于制度意图发生", "现有证据不足以锁定责任"],
        ),
    )

    def build_context(
        self,
        observations: list[Observation],
        evidence: list[Evidence],
        information_boundaries: list[InformationBoundary],
        subjective_models: list[SubjectiveWorldModel],
        step: int,
    ) -> PossibleWorldContext:
        observations_by_id = {item.observation_id: item for item in observations}
        boundaries = {item.agent_id: item for item in information_boundaries}
        all_worlds = []
        all_assessments = []
        priors = []
        posteriors = []
        revisions = []
        new_beliefs = []

        for model in subjective_models:
            boundary = boundaries[model.agent_id]
            visible_observation_ids = [
                observation_id
                for observation_id in boundary.observation_ids
                if observation_id in observations_by_id
            ]
            visible_evidence = [
                item
                for item in evidence
                if item.agent_id == model.agent_id
                and item.observation_id in visible_observation_ids
            ]
            worlds = self._build_worlds(
                model,
                boundary,
                visible_observation_ids,
                step,
            )
            prior = self._build_prior(model, boundary, worlds, step)
            assessments = [
                self._assess_evidence(world, item, model, boundary)
                for world in worlds
                for item in visible_evidence
            ]
            posterior, revision = self.revise(prior, worlds, assessments)
            dominant_world = next(
                item
                for item in worlds
                if item.possible_world_id == posterior.dominant_possible_world_id
            )
            new_belief = PossibleWorldBelief(
                belief_id=f"possible_world_belief_{step:03d}_{model.agent_id}",
                agent_id=model.agent_id,
                step=step,
                possible_world_id=dominant_world.possible_world_id,
                proposition=dominant_world.proposition,
                confidence=posterior.probabilities[dominant_world.possible_world_id],
                uncertainty=posterior.uncertainty,
                belief_distribution_id=posterior.distribution_id,
                source_observation_ids=visible_observation_ids,
                source_evidence_ids=[item.evidence_id for item in visible_evidence],
                source_revision_id=revision.revision_id,
            )

            all_worlds.extend(worlds)
            all_assessments.extend(assessments)
            priors.append(prior)
            posteriors.append(posterior)
            revisions.append(revision)
            new_beliefs.append(new_belief)

        return PossibleWorldContext(
            possible_worlds=all_worlds,
            evidence_assessments=all_assessments,
            prior_distributions=priors,
            revisions=revisions,
            posterior_distributions=posteriors,
            new_beliefs=new_beliefs,
        )

    def revise(
        self,
        prior: BeliefDistribution,
        worlds: list[PossibleWorld],
        assessments: list[WorldEvidenceAssessment],
    ) -> tuple[BeliefDistribution, BayesianWorldRevision]:
        assessments_by_world: dict[str, list[WorldEvidenceAssessment]] = {}
        for assessment in assessments:
            assessments_by_world.setdefault(assessment.possible_world_id, []).append(
                assessment
            )

        eliminated = sorted(
            world.possible_world_id
            for world in worlds
            if any(
                item.rules_out_world
                for item in assessments_by_world.get(world.possible_world_id, [])
            )
        )
        unnormalized = {}
        for world in worlds:
            world_id = world.possible_world_id
            if world_id in eliminated:
                unnormalized[world_id] = 0.0
                continue
            likelihood = 1.0
            for assessment in assessments_by_world.get(world_id, []):
                likelihood *= assessment.likelihood
            unnormalized[world_id] = prior.probabilities[world_id] * likelihood

        normalization = sum(unnormalized.values())
        if normalization <= 0.0:
            raise ValueError("evidence eliminated every possible world")
        probabilities = {
            world_id: value / normalization
            for world_id, value in unnormalized.items()
        }
        dominant_world_id = max(probabilities, key=probabilities.get)
        posterior_id = prior.distribution_id.replace("prior", "posterior")
        source_evidence_ids = sorted({item.evidence_id for item in assessments})
        posterior = BeliefDistribution(
            distribution_id=posterior_id,
            agent_id=prior.agent_id,
            step=prior.step,
            stage="posterior",
            information_boundary_id=prior.information_boundary_id,
            probabilities=probabilities,
            source_evidence_ids=source_evidence_ids,
            eliminated_world_ids=eliminated,
            dominant_possible_world_id=dominant_world_id,
            uncertainty=self._normalized_entropy(probabilities),
        )
        revision = BayesianWorldRevision(
            revision_id=f"world_revision_{prior.step:03d}_{prior.agent_id}",
            agent_id=prior.agent_id,
            step=prior.step,
            prior_distribution_id=prior.distribution_id,
            posterior_distribution_id=posterior.distribution_id,
            evidence_assessment_ids=[item.assessment_id for item in assessments],
            eliminated_world_ids=eliminated,
            normalization_constant=normalization,
        )
        return posterior, revision

    def _build_worlds(
        self,
        model: SubjectiveWorldModel,
        boundary: InformationBoundary,
        observation_ids: list[str],
        step: int,
    ) -> list[PossibleWorld]:
        return [
            PossibleWorld(
                possible_world_id=(
                    f"possible_world_{step:03d}_{model.agent_id}_{kind}"
                ),
                agent_id=model.agent_id,
                step=step,
                kind=kind,
                proposition=proposition,
                assumptions=assumptions,
                source_observation_ids=observation_ids,
                information_boundary_id=boundary.information_boundary_id,
            )
            for kind, proposition, assumptions in self.WORLD_TEMPLATES
        ]

    def _build_prior(
        self,
        model: SubjectiveWorldModel,
        boundary: InformationBoundary,
        worlds: list[PossibleWorld],
        step: int,
    ) -> BeliefDistribution:
        safety = self._value_weight(model, "safety")
        order = self._value_weight(model, "order")
        raw = {
            "institutional_monitoring": (
                0.2
                + ((1.0 - model.epistemology.trust_authority) * 0.35)
                + (model.theory_of_change.institutions * 0.15)
            ),
            "protective_security": (
                0.2
                + (model.epistemology.trust_authority * 0.35)
                + (((safety + order) / 2.0) * 0.15)
            ),
            "technical_anomaly": (
                0.2
                + (model.epistemology.tolerance_for_uncertainty * 0.3)
                + (model.theory_of_change.contingency * 0.15)
            ),
        }
        probabilities = self._normalize(
            {world.possible_world_id: raw[world.kind] for world in worlds}
        )
        dominant = max(probabilities, key=probabilities.get)
        return BeliefDistribution(
            distribution_id=f"possible_world_prior_{step:03d}_{model.agent_id}",
            agent_id=model.agent_id,
            step=step,
            stage="prior",
            information_boundary_id=boundary.information_boundary_id,
            probabilities=probabilities,
            dominant_possible_world_id=dominant,
            uncertainty=self._normalized_entropy(probabilities),
        )

    def _assess_evidence(
        self,
        world: PossibleWorld,
        evidence: Evidence,
        model: SubjectiveWorldModel,
        boundary: InformationBoundary,
    ) -> WorldEvidenceAssessment:
        signal = (evidence.reliability * 0.45) + (evidence.strength * 0.55)
        opacity = 1.0 - boundary.coverage
        if world.kind == "institutional_monitoring":
            likelihood = 0.4 + (signal * 0.35) + (opacity * 0.15)
        elif world.kind == "protective_security":
            authority_signal = (
                model.epistemology.trust_authority
                if evidence.evidence_type == "authority"
                else 1.0 - model.epistemology.trust_authority
            )
            likelihood = 0.35 + (authority_signal * 0.3) + (signal * 0.15)
        else:
            likelihood = (
                0.35
                + (model.epistemology.tolerance_for_uncertainty * 0.2)
                + ((1.0 - signal) * 0.2)
            )
        likelihood = self._clamp(likelihood, minimum=0.02)
        if evidence.polarity == "contradicts":
            likelihood = self._clamp(1.0 - likelihood, minimum=0.02)
        compatibility = (
            "supports"
            if likelihood >= 0.67
            else "contradicts" if likelihood <= 0.33 else "neutral"
        )
        rules_out = (
            compatibility == "contradicts"
            and likelihood <= 0.05
            and evidence.reliability >= 0.98
            and evidence.strength >= 0.98
        )
        return WorldEvidenceAssessment(
            assessment_id=(
                f"world_evidence_{world.step:03d}_{world.agent_id}_"
                f"{world.kind}_{evidence.evidence_id}"
            ),
            possible_world_id=world.possible_world_id,
            evidence_id=evidence.evidence_id,
            compatibility=compatibility,
            likelihood=likelihood,
            rules_out_world=rules_out,
            rationale=(
                f"kind={world.kind}; signal={signal:.3f}; "
                f"boundary-opacity={opacity:.3f}; polarity={evidence.polarity}."
            ),
        )

    def _normalized_entropy(self, probabilities: dict[str, float]) -> float:
        active = [value for value in probabilities.values() if value > 0.0]
        if len(active) <= 1:
            return 0.0
        entropy = -sum(value * log(value) for value in active)
        return entropy / log(len(active))

    def _normalize(self, values: dict[str, float]) -> dict[str, float]:
        total = sum(values.values())
        if total <= 0.0:
            raise ValueError("possible-world prior weights must be positive")
        return {key: value / total for key, value in values.items()}

    def _value_weight(self, model: SubjectiveWorldModel, name: str) -> float:
        value = model.values.get(name)
        return value.base_weight if value else 0.5

    def _clamp(self, value: float, minimum: float = 0.0) -> float:
        return min(1.0, max(minimum, value))
