import argparse
import hashlib
import json
from pathlib import Path

from core.cognition_engine import CognitionEngine
from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer
from schemas import (
    CognitiveCondition,
    CognitiveExperimentTrial,
    Epistemology,
    EpistemologySwapResult,
    ExperimentalAction,
    ExperimentMetric,
    Observation,
    PartialObservabilityControl,
    SameWorldDifferentMindsResult,
    SubjectiveWorldModel,
    Value,
)


DEFAULT_RESULT_DIR = Path(__file__).resolve().parent / "results"


class SameWorldDifferentMindsExperiment:
    """Run Day 10's controlled cognitive-difference experiment."""

    ACTION_BY_IMPLICATION = {
        "collect evidence secretly": "secretly_collect_network_evidence",
        "follow institutional guidance": "follow_institutional_guidance",
        "seek additional evidence": "seek_additional_evidence",
        "seek independent evidence": "seek_independent_evidence",
    }

    def run(
        self,
        *,
        export: bool = False,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> SameWorldDifferentMindsResult:
        objective_state, _, scenario_models = WorldInitializer().initialize("校园监控")
        fingerprint = self._world_fingerprint(objective_state)
        conditions = self._conditions()
        observations = [
            self._shared_observation(condition.condition_id, objective_state.step)
            for condition in conditions
        ]
        models = [self._model_for(condition) for condition in conditions]
        cognition = CognitionEngine().interpret(observations, models)

        trials = self._build_trials(
            conditions=conditions,
            observations=observations,
            cognition=cognition,
            objective_state_id=objective_state.state_id,
            fingerprint=fingerprint,
        )
        metrics = self._metrics(trials)
        swaps = self._run_epistemology_swap(conditions, trials, objective_state.step)
        partial_control = self._partial_observability_control(
            objective_state,
            scenario_models,
        )
        passed = (
            all(metric.passed for metric in metrics)
            and all(item.changed_as_predicted for item in swaps)
            and partial_control.boundary_preserved
        )
        result = SameWorldDifferentMindsResult(
            experiment_id="experiment_01_same_world_different_minds",
            hypothesis=(
                "在相同客观世界和相同观察下，仅改变主体认知配置，"
                "会产生可归因的不同信念、解释与行动。"
            ),
            controlled_variables=[
                "objective_world",
                "observation_content",
                "observation_source",
                "evidence_type",
                "observation_reliability",
                "initial_belief_prior",
                "deterministic_runtime",
            ],
            independent_variable="cognitive_configuration",
            objective_state_id=objective_state.state_id,
            objective_world_fingerprint=fingerprint,
            shared_observation_signature=self._observation_signature(observations[0]),
            trials=trials,
            metrics=metrics,
            epistemology_swap=swaps,
            partial_observability_control=partial_control,
            passed=passed,
        )
        if export:
            self.export(result, output_dir)
        return result

    def export(
        self,
        result: SameWorldDifferentMindsResult,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> tuple[Path, Path]:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        json_path = destination / "experiment_01.json"
        report_path = destination / "experiment_01.md"
        json_path.write_text(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report_path.write_text(self.render_report(result), encoding="utf-8")
        return json_path, report_path

    def render_report(self, result: SameWorldDifferentMindsResult) -> str:
        status = "PASS" if result.passed else "FAIL"
        lines = [
            "# Experiment 01: Same World, Different Minds",
            "",
            f"**实验状态：{status}**",
            "",
            "## 研究问题",
            "",
            result.hypothesis,
            "",
            "## 实验控制",
            "",
            f"- 客观状态：`{result.objective_state_id}`",
            f"- 世界指纹：`{result.objective_world_fingerprint}`",
            f"- 自变量：`{result.independent_variable}`",
            f"- 固定变量：{', '.join(result.controlled_variables)}",
            f"- 共享观察：{result.shared_observation_signature['content']}",
            "",
            "三个条件接收内容、来源、证据类型、可靠度和 provenance 完全相同的观察；"
            "仅 `agent_id` 与记录 ID 为维持引用完整性而不同。",
            "",
            "## 主实验结果",
            "",
            "| 认知配置 | 证据权重 | 后验信念 | Bias | Interpretation | Action |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
        for trial in result.trials:
            bias = trial.bias_filter_result.applied_biases[0].bias_type
            lines.append(
                "| {label} | {strength:.3f} | {belief} ({posterior:.3f}) | "
                "{bias} | {meaning} | `{action}` |".format(
                    label=trial.condition.label,
                    strength=trial.evidence.strength,
                    belief=trial.belief.proposition,
                    posterior=trial.belief_update.posterior,
                    bias=bias,
                    meaning=trial.interpretation.meaning,
                    action=trial.action.action,
                )
            )

        lines.extend(
            [
                "",
                "## 定量验收",
                "",
                "| 指标 | 值 | 结果 | 说明 |",
                "| --- | ---: | :---: | --- |",
            ]
        )
        for metric in result.metrics:
            lines.append(
                f"| {metric.metric} | {metric.value:.3f} | "
                f"{'PASS' if metric.passed else 'FAIL'} | {metric.detail} |"
            )

        lines.extend(
            [
                "",
                "## 参数交换实验",
                "",
                "只交换 Dataist 与 Institutionalist 的 Epistemology，其他 Value 配置保持不变。",
                "",
                "| 配置 | 借用参数 | 原解释 / 行动 | 交换后解释 / 行动 | 结果 |",
                "| --- | --- | --- | --- | :---: |",
            ]
        )
        for item in result.epistemology_swap:
            lines.append(
                f"| {item.condition_id} | {item.borrowed_epistemology_from} | "
                f"{item.baseline_meaning} / `{item.baseline_action}` | "
                f"{item.swapped_meaning} / `{item.swapped_action}` | "
                f"{'PASS' if item.changed_as_predicted else 'FAIL'} |"
            )

        control = result.partial_observability_control
        lines.extend(
            [
                "",
                "## Partial Observability 对照",
                "",
                "该对照独立于主实验，用于确认信息差来自可见性规则，而不是认知参数。",
                "",
                "| Agent | Public | Private |",
                "| --- | --- | --- |",
            ]
        )
        agent_ids = sorted(control.public_information_ids_by_agent)
        for agent_id in agent_ids:
            public_ids = ", ".join(control.public_information_ids_by_agent[agent_id]) or "-"
            private_ids = ", ".join(control.private_information_ids_by_agent[agent_id]) or "-"
            lines.append(f"| {agent_id} | {public_ids} | {private_ids} |")
        lines.extend(
            [
                "",
                f"- 被观察到的 hidden information："
                f"{', '.join(control.hidden_information_ids_observed) or '无'}",
                f"- 信息边界：{'PASS' if control.boundary_preserved else 'FAIL'}",
                "",
                "## 结论",
                "",
                "H1 在当前确定性校园监控基线上得到支持：共享观察保持一致时，"
                "三种认知配置产生了不同的信念命题、解释框架和行动建议；"
                "参数交换进一步表明变化可归因于显式 Epistemology，而非输入信息差。",
                "",
                "本实验验证的是当前规则模型内部的因果敏感性，不代表对真实人类认知的外部有效性。"
                "后续仍需扩大场景、重复样本并加入人工评分。",
                "",
            ]
        )
        return "\n".join(lines)

    def _conditions(self) -> list[CognitiveCondition]:
        return [
            CognitiveCondition(
                condition_id="dataist",
                label="数据主义者",
                values={
                    "freedom": Value(base_weight=0.90),
                    "truth": Value(base_weight=0.92),
                    "safety": Value(base_weight=0.40),
                    "order": Value(base_weight=0.30),
                },
                epistemology=Epistemology(
                    trust_data=0.95,
                    trust_authority=0.15,
                    tolerance_for_uncertainty=0.55,
                ),
            ),
            CognitiveCondition(
                condition_id="institutionalist",
                label="制度主义者",
                values={
                    "freedom": Value(base_weight=0.40),
                    "truth": Value(base_weight=0.55),
                    "safety": Value(base_weight=0.90),
                    "order": Value(base_weight=0.85),
                },
                epistemology=Epistemology(
                    trust_data=0.40,
                    trust_authority=0.90,
                    tolerance_for_uncertainty=0.35,
                ),
            ),
            CognitiveCondition(
                condition_id="skeptic",
                label="怀疑主义者",
                values={
                    "freedom": Value(base_weight=0.55),
                    "truth": Value(base_weight=0.95),
                    "safety": Value(base_weight=0.50),
                    "order": Value(base_weight=0.45),
                },
                epistemology=Epistemology(
                    trust_data=0.35,
                    trust_authority=0.20,
                    tolerance_for_uncertainty=0.85,
                ),
            ),
        ]

    def _shared_observation(self, agent_id: str, step: int) -> Observation:
        return Observation(
            observation_id=f"obs_experiment_01_{agent_id}",
            information_id="info_experiment_network_monitoring_increase",
            agent_id=agent_id,
            step=step,
            source="network_status_dashboard",
            evidence_type="data",
            content="Network monitoring increased.",
            reliability=0.90,
            visibility="public",
            provenance=["experiment_control", "campus_network_monitoring_rollout"],
        )

    def _model_for(self, condition: CognitiveCondition) -> SubjectiveWorldModel:
        return SubjectiveWorldModel(
            agent_id=condition.condition_id,
            values=condition.values,
            epistemology=condition.epistemology,
            goals=["understand the network monitoring change"],
        )

    def _build_trials(
        self,
        *,
        conditions: list[CognitiveCondition],
        observations: list[Observation],
        cognition,
        objective_state_id: str,
        fingerprint: str,
    ) -> list[CognitiveExperimentTrial]:
        models = {model.agent_id: model for model in cognition.subjective_models}
        evidence = {item.agent_id: item for item in cognition.evidence}
        updates = {item.agent_id: item for item in cognition.belief_updates}
        belief_states = {item.agent_id: item for item in cognition.belief_states}
        mental_models = {item.agent_id: item for item in cognition.mental_models}
        interpretations = {item.agent_id: item for item in cognition.interpretations}
        bias_by_id = {item.bias_filter_id: item for item in cognition.bias_results}
        observations_by_agent = {item.agent_id: item for item in observations}
        trials = []
        for condition in conditions:
            interpretation = interpretations[condition.condition_id]
            action = self._action_for(interpretation.action_implication)
            belief = models[condition.condition_id].beliefs[-1]
            trials.append(
                CognitiveExperimentTrial(
                    condition=condition,
                    objective_state_id=objective_state_id,
                    objective_world_fingerprint=fingerprint,
                    observation=observations_by_agent[condition.condition_id],
                    evidence=evidence[condition.condition_id],
                    belief=belief,
                    belief_update=updates[condition.condition_id],
                    belief_state=belief_states[condition.condition_id],
                    mental_model=mental_models[condition.condition_id],
                    bias_filter_result=bias_by_id[interpretation.bias_filter_id],
                    interpretation=interpretation,
                    action=ExperimentalAction(
                        action=action,
                        source_interpretation_id=interpretation.interpretation_id,
                        rationale=(
                            f"Policy mapping from action implication: "
                            f"{interpretation.action_implication}"
                        ),
                    ),
                )
            )
        return trials

    def _metrics(self, trials: list[CognitiveExperimentTrial]) -> list[ExperimentMetric]:
        count = len(trials)
        signatures = {
            json.dumps(self._observation_signature(item.observation), sort_keys=True)
            for item in trials
        }
        belief_count = len({item.belief.proposition for item in trials})
        meaning_count = len({item.interpretation.meaning for item in trials})
        action_count = len({item.action.action for item in trials})
        return [
            ExperimentMetric(
                metric="observation_equivalence",
                value=1.0 if len(signatures) == 1 else 0.0,
                passed=len(signatures) == 1,
                detail="Normalized observation signatures are identical.",
            ),
            ExperimentMetric(
                metric="belief_diversity",
                value=belief_count / count,
                passed=belief_count == count,
                detail=f"{belief_count}/{count} unique belief propositions.",
            ),
            ExperimentMetric(
                metric="interpretation_diversity",
                value=meaning_count / count,
                passed=meaning_count == count,
                detail=f"{meaning_count}/{count} unique meanings.",
            ),
            ExperimentMetric(
                metric="action_diversity",
                value=action_count / count,
                passed=action_count == count,
                detail=f"{action_count}/{count} unique selected actions.",
            ),
        ]

    def _run_epistemology_swap(
        self,
        conditions: list[CognitiveCondition],
        baseline_trials: list[CognitiveExperimentTrial],
        step: int,
    ) -> list[EpistemologySwapResult]:
        condition_by_id = {item.condition_id: item for item in conditions}
        baseline_by_id = {item.condition.condition_id: item for item in baseline_trials}
        pairs = [
            ("dataist", "institutionalist"),
            ("institutionalist", "dataist"),
        ]
        results = []
        for condition_id, donor_id in pairs:
            base = condition_by_id[condition_id]
            swapped = base.model_copy(
                update={"epistemology": condition_by_id[donor_id].epistemology.model_copy(deep=True)}
            )
            observation = self._shared_observation(condition_id, step)
            cognition = CognitionEngine().interpret(
                [observation],
                [self._model_for(swapped)],
            )
            interpretation = cognition.interpretations[0]
            action = self._action_for(interpretation.action_implication)
            baseline = baseline_by_id[condition_id]
            results.append(
                EpistemologySwapResult(
                    condition_id=condition_id,
                    borrowed_epistemology_from=donor_id,
                    baseline_meaning=baseline.interpretation.meaning,
                    swapped_meaning=interpretation.meaning,
                    baseline_action=baseline.action.action,
                    swapped_action=action,
                    changed_as_predicted=(
                        interpretation.meaning != baseline.interpretation.meaning
                        and action != baseline.action.action
                    ),
                )
            )
        return results

    def _partial_observability_control(
        self,
        objective_state,
        scenario_models: list[SubjectiveWorldModel],
    ) -> PartialObservabilityControl:
        observations = ObservationEngine().observe(objective_state, scenario_models)
        public_by_agent = {model.agent_id: [] for model in scenario_models}
        private_by_agent = {model.agent_id: [] for model in scenario_models}
        hidden_ids = []
        for observation in observations:
            if observation.visibility == "public":
                public_by_agent[observation.agent_id].append(observation.information_id)
            elif observation.visibility == "private":
                private_by_agent[observation.agent_id].append(observation.information_id)
            elif observation.visibility == "hidden":
                hidden_ids.append(observation.information_id)
        for values in [*public_by_agent.values(), *private_by_agent.values()]:
            values.sort()

        lin_private = private_by_agent.get("lin_xia", [])
        wang_private = private_by_agent.get("wang_chen", [])
        public_sets = {tuple(items) for items in public_by_agent.values()}
        boundary_preserved = (
            len(public_sets) == 1
            and "info_private_dns_redirect" in lin_private
            and "info_private_dns_redirect" not in wang_private
            and not hidden_ids
        )
        return PartialObservabilityControl(
            public_information_ids_by_agent=public_by_agent,
            private_information_ids_by_agent=private_by_agent,
            hidden_information_ids_observed=hidden_ids,
            boundary_preserved=boundary_preserved,
        )

    def _action_for(self, implication: str) -> str:
        try:
            return self.ACTION_BY_IMPLICATION[implication]
        except KeyError as error:
            raise ValueError(f"No experimental action policy for {implication!r}") from error

    def _observation_signature(self, observation: Observation) -> dict[str, object]:
        return {
            "information_id": observation.information_id,
            "step": observation.step,
            "source": observation.source,
            "evidence_type": observation.evidence_type,
            "content": observation.content,
            "reliability": observation.reliability,
            "visibility": observation.visibility,
            "location_id": observation.location_id,
            "provenance": observation.provenance,
        }

    def _world_fingerprint(self, objective_state) -> str:
        payload = json.dumps(
            objective_state.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Experiment 01: Same World, Different Minds"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULT_DIR)
    args = parser.parse_args()
    experiment = SameWorldDifferentMindsExperiment()
    result = experiment.run(export=True, output_dir=args.output_dir)
    print(
        json.dumps(
            {
                "experiment_id": result.experiment_id,
                "passed": result.passed,
                "output_dir": str(args.output_dir),
                "metrics": [item.model_dump(mode="json") for item in result.metrics],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
