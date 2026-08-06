import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from app import run_pipeline
from schemas import (
    ExperimentMetric,
    WorldModelComparison,
    WorldModelConditionResult,
    WorldModelExperimentResult,
)


DEFAULT_RESULT_DIR = Path(__file__).resolve().parent / "results"


class WorldModelAblationExperiment:
    """Compare multi-step rollouts with and without configured subjectivity."""

    def run(
        self,
        *,
        steps: int = 3,
        export: bool = False,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> WorldModelExperimentResult:
        if not 3 <= steps <= 5:
            raise ValueError("world model experiment requires 3 to 5 steps")
        with_model = self._run_condition(
            "with_subjective_model",
            True,
            steps,
        )
        without_model = self._run_condition(
            "without_subjective_model",
            False,
            steps,
        )
        comparison = self._compare(with_model, without_model)
        metrics = self._metrics(comparison)
        result = WorldModelExperimentResult(
            experiment_id="day30_world_model_ablation",
            hypothesis=(
                "在客观世界、可见性边界、运行步数和推演模块不变时，移除"
                "主体的个体知识、价值、目标与认识论先验，应改变信念、解释"
                "或行动评估轨迹。"
            ),
            controlled_variables=[
                "initial_objective_world",
                "agent_ids_and_roles",
                "information_visibility",
                "three_step_horizon",
                "enabled_lenses",
                "future_templates",
                "decision_weights",
                "deterministic_runtime",
            ],
            independent_variable="configured_subjective_world_models",
            with_subjective_model=with_model,
            without_subjective_model=without_model,
            comparison=comparison,
            metrics=metrics,
            passed=comparison.passed,
        )
        if export:
            self.export(result, output_dir)
        return result

    def export(
        self,
        result: WorldModelExperimentResult,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> tuple[Path, Path]:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        json_path = destination / "world_model_ablation.json"
        report_path = destination / "world_model_ablation.md"
        json_path.write_text(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report_path.write_text(self._report(result), encoding="utf-8")
        return json_path, report_path

    def _run_condition(
        self,
        condition_id: str,
        use_subjective_models: bool,
        steps: int,
    ) -> WorldModelConditionResult:
        output = run_pipeline(
            "校园监控",
            steps=steps,
            export=False,
            use_subjective_models=use_subjective_models,
        )
        futures_by_id = {
            item["future_id"]: item for item in output["candidate_futures"]
        }
        selected_future_ids = [
            item["future_id"] for item in output["selected_futures"]
        ]
        return WorldModelConditionResult(
            condition_id=condition_id,
            subjective_models_enabled=use_subjective_models,
            steps=steps,
            initial_world_fingerprint=self._fingerprint(
                output["objective_states"][0]
            ),
            subjective_model_fingerprint=self._fingerprint(
                self._subjective_configuration(output, use_subjective_models)
            ),
            observation_fingerprint=self._fingerprint(
                self._observation_signature(output)
            ),
            belief_trajectory_fingerprint=self._fingerprint(
                {
                    "belief_states": output["belief_states"],
                    "possible_world_beliefs": output["possible_world_beliefs"],
                }
            ),
            interpretation_trajectory_fingerprint=self._fingerprint(
                output["interpretations"]
            ),
            future_scores=self._scores_by_step(
                output["future_scores"],
                "future_id",
                "score",
                steps,
            ),
            action_scores=self._scores_by_step(
                output["value_assessments"],
                "action",
                "score",
                steps,
            ),
            selected_actions=[
                item["selected_action"] for item in output["decisions"]
            ],
            selected_mechanisms=[
                futures_by_id[item]["mechanism"]["mechanism_type"]
                for item in selected_future_ids
            ],
            state_change_paths=[
                change["path"]
                for future in output["selected_futures"]
                for change in future["expected_state_changes"]
            ],
            final_state_fingerprint=self._fingerprint(
                self._factual_state(output["objective_states"][-1])
            ),
            provenance_fingerprint=self._fingerprint(
                self._provenance_signature(output)
            ),
            provenance_complete=self._provenance_complete(output),
        )

    def _compare(
        self,
        with_model: WorldModelConditionResult,
        without_model: WorldModelConditionResult,
    ) -> WorldModelComparison:
        objective_control = (
            with_model.initial_world_fingerprint
            == without_model.initial_world_fingerprint
        )
        observation_control = (
            with_model.observation_fingerprint
            == without_model.observation_fingerprint
        )
        subjective_removed = (
            with_model.subjective_model_fingerprint
            != without_model.subjective_model_fingerprint
            and not without_model.subjective_models_enabled
        )
        belief_changed = (
            with_model.belief_trajectory_fingerprint
            != without_model.belief_trajectory_fingerprint
        )
        interpretation_changed = (
            with_model.interpretation_trajectory_fingerprint
            != without_model.interpretation_trajectory_fingerprint
        )
        future_scores_changed = (
            with_model.future_scores != without_model.future_scores
        )
        action_scores_changed = (
            with_model.action_scores != without_model.action_scores
        )
        selected_actions_changed = (
            with_model.selected_actions != without_model.selected_actions
        )
        mechanisms_changed = (
            with_model.selected_mechanisms
            != without_model.selected_mechanisms
        )
        final_state_changed = (
            with_model.final_state_fingerprint
            != without_model.final_state_fingerprint
        )
        provenance_changed = (
            with_model.provenance_fingerprint
            != without_model.provenance_fingerprint
        )
        effect_detected = any(
            (
                belief_changed,
                interpretation_changed,
                future_scores_changed,
                action_scores_changed,
                selected_actions_changed,
                mechanisms_changed,
                final_state_changed,
                provenance_changed,
            )
        )
        provenance_preserved = (
            with_model.provenance_complete
            and without_model.provenance_complete
        )
        passed = all(
            (
                objective_control,
                observation_control,
                subjective_removed,
                belief_changed,
                interpretation_changed,
                future_scores_changed,
                action_scores_changed,
                effect_detected,
                provenance_preserved,
            )
        )
        return WorldModelComparison(
            objective_control_preserved=objective_control,
            observation_boundary_preserved=observation_control,
            subjective_configuration_removed=subjective_removed,
            belief_trajectory_changed=belief_changed,
            interpretation_trajectory_changed=interpretation_changed,
            future_scores_changed=future_scores_changed,
            action_scores_changed=action_scores_changed,
            selected_actions_changed=selected_actions_changed,
            selected_mechanisms_changed=mechanisms_changed,
            final_state_changed=final_state_changed,
            provenance_changed=provenance_changed,
            subjective_effect_detected=effect_detected,
            provenance_preserved=provenance_preserved,
            passed=passed,
        )

    def _metrics(
        self,
        comparison: WorldModelComparison,
    ) -> list[ExperimentMetric]:
        checks = [
            (
                "objective_control_preserved",
                comparison.objective_control_preserved,
                "Both conditions start from the same objective world.",
            ),
            (
                "observation_boundary_preserved",
                comparison.observation_boundary_preserved,
                "Both conditions receive the same visible observations.",
            ),
            (
                "belief_trajectory_changed",
                comparison.belief_trajectory_changed,
                "Removing configured subjectivity changes belief dynamics.",
            ),
            (
                "interpretation_trajectory_changed",
                comparison.interpretation_trajectory_changed,
                "Removing configured subjectivity changes interpretation.",
            ),
            (
                "decision_scores_changed",
                comparison.future_scores_changed
                and comparison.action_scores_changed,
                "Future and action evaluations respond to the ablation.",
            ),
            (
                "provenance_preserved",
                comparison.provenance_preserved,
                "Both conditions retain complete transition provenance.",
            ),
        ]
        return [
            ExperimentMetric(
                metric=name,
                value=1.0 if passed else 0.0,
                passed=passed,
                detail=detail,
            )
            for name, passed, detail in checks
        ]

    def _scores_by_step(
        self,
        items: list[dict[str, Any]],
        key_field: str,
        score_field: str,
        steps: int,
    ) -> list[dict[str, float]]:
        return [
            {
                item[key_field]: item[score_field]
                for item in items
                if self._item_step(item) == step
            }
            for step in range(1, steps + 1)
        ]

    def _item_step(self, item: dict[str, Any]) -> int:
        if "step" in item:
            return int(item["step"])
        identifier = str(item.get("value_assessment_id", ""))
        parts = identifier.split("_")
        if len(parts) >= 3 and parts[1].isdigit():
            return int(parts[1])
        raise ValueError("experiment artifact does not expose a simulation step")

    def _subjective_configuration(
        self,
        output: dict[str, Any],
        enabled: bool,
    ) -> Any:
        if enabled:
            return [
                {
                    "agent_id": item["agent_id"],
                    "values": item["values"],
                    "goals": item["goals"],
                    "epistemology": item["epistemology"],
                    "human_nature_model": item["human_nature_model"],
                    "theory_of_change": item["theory_of_change"],
                }
                for item in output["agent_profiles"]
            ]
        return [
            {
                "agent_id": item["agent_id"],
                "roles": item["roles"],
                "configured_subjectivity": False,
            }
            for item in output["agent_profiles"]
        ]

    def _observation_signature(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        fields = (
            "agent_id",
            "step",
            "information_id",
            "content",
            "reliability",
            "visibility",
        )
        return [
            {field: item[field] for field in fields}
            for item in output["observations"]
            if item["step"] == 0
        ]

    def _factual_state(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in state.items()
            if key not in {"state_id", "step", "timestamp", "events", "history"}
        }

    def _provenance_signature(self, output: dict[str, Any]) -> list[dict[str, Any]]:
        fields = (
            "step",
            "path",
            "cause",
            "supporting_hypothesis_ids",
            "opposing_hypothesis_ids",
            "supporting_lens_names",
            "supporting_belief_ids",
            "supporting_goals",
            "constraint_ids",
        )
        return [
            {field: item[field] for field in fields}
            for item in output["state_provenance"]
            if item["source"] == "world_transition"
        ]

    def _provenance_complete(self, output: dict[str, Any]) -> bool:
        records = [
            item
            for item in output["state_provenance"]
            if item["source"] == "world_transition"
        ]
        return bool(records) and all(
            item["source_state_id"]
            and item["target_state_id"]
            and item["future_id"]
            and item["future_evaluation_id"]
            and item["event_id"]
            and item["action_ids"]
            and item["decision_ids"]
            and item["source_observation_ids"]
            and item["supporting_belief_ids"]
            and item["constraint_ids"]
            and item["old_value"] != item["new_value"]
            for item in records
        )

    def _fingerprint(self, value: Any) -> str:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _report(self, result: WorldModelExperimentResult) -> str:
        comparison = result.comparison
        return "\n".join(
            [
                "# Day 30 World Model Ablation",
                "",
                f"- Hypothesis: {result.hypothesis}",
                f"- Objective control preserved: {comparison.objective_control_preserved}",
                f"- Observation boundary preserved: {comparison.observation_boundary_preserved}",
                f"- Belief trajectory changed: {comparison.belief_trajectory_changed}",
                f"- Interpretation changed: {comparison.interpretation_trajectory_changed}",
                f"- Future scores changed: {comparison.future_scores_changed}",
                f"- Action scores changed: {comparison.action_scores_changed}",
                f"- Selected actions changed: {comparison.selected_actions_changed}",
                f"- Final factual state changed: {comparison.final_state_changed}",
                f"- Provenance preserved: {comparison.provenance_preserved}",
                f"- Passed: {result.passed}",
                "",
                "The no-subjective-model condition retains neutral agent carriers "
                "for interface compatibility while removing configured knowledge, "
                "values, goals, beliefs, and epistemological preferences.",
                "",
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Day 30 experiment")
    parser.add_argument("--steps", type=int, default=3, choices=range(3, 6))
    parser.add_argument("--output-dir", default=str(DEFAULT_RESULT_DIR))
    args = parser.parse_args()
    result = WorldModelAblationExperiment().run(
        steps=args.steps,
        export=True,
        output_dir=args.output_dir,
    )
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
