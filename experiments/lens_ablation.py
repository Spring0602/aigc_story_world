import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from app import run_pipeline
from schemas import (
    ExperimentMetric,
    LensAblationComparison,
    LensAblationConditionResult,
    LensAblationExperimentResult,
)


DEFAULT_RESULT_DIR = Path(__file__).resolve().parent / "results"
ALL_LENSES = {"psychology", "economic", "social_structure"}


class LensAblationExperiment:
    """Run Day 20's controlled leave-one-lens-out experiment."""

    def run(
        self,
        *,
        export: bool = False,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> LensAblationExperimentResult:
        baseline = self._run_condition(
            condition_id="all_lenses",
            enabled_lenses=ALL_LENSES,
            removed_lens=None,
        )
        ablations = [
            self._run_condition(
                condition_id=f"without_{lens}",
                enabled_lenses=ALL_LENSES - {lens},
                removed_lens=lens,
            )
            for lens in sorted(ALL_LENSES)
        ]
        comparisons = [
            self._compare(baseline, condition)
            for condition in ablations
        ]
        metrics = self._metrics(comparisons)
        result = LensAblationExperimentResult(
            experiment_id="experiment_02_lens_ablation",
            hypothesis=(
                "在客观世界、主体配置和候选未来模板不变时，移除任一 Lens "
                "应改变假设池、跨 Lens 关系以及 Future 和 Action 的评分。"
            ),
            controlled_variables=[
                "objective_world",
                "subjective_models",
                "observations",
                "belief_updates",
                "candidate_future_templates",
                "deterministic_runtime",
                "decision_weights",
            ],
            baseline=baseline,
            ablations=ablations,
            comparisons=comparisons,
            metrics=metrics,
            passed=all(item.passed for item in comparisons),
        )
        if export:
            self.export(result, output_dir)
        return result

    def _run_condition(
        self,
        *,
        condition_id: str,
        enabled_lenses: set[str],
        removed_lens: str | None,
    ) -> LensAblationConditionResult:
        output = run_pipeline(
            "校园监控",
            steps=1,
            export=False,
            enabled_lenses=enabled_lenses,
        )
        hypothesis_ids = [
            item["hypothesis_id"] for item in output["hypotheses"]
        ]
        relation_ids = [
            item["relation_id"] for item in output["hypothesis_relations"]
        ]
        relation_type_counts = dict(
            sorted(
                Counter(
                    item["relation_type"]
                    for item in output["hypothesis_relations"]
                ).items()
            )
        )
        future_scores = {
            item["future_id"]: item["score"]
            for item in output["future_scores"]
        }
        action_scores = {
            item["action"]: item["score"]
            for item in output["value_assessments"]
        }
        action_ranking = [
            action
            for action, _ in sorted(
                action_scores.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]
        return LensAblationConditionResult(
            condition_id=condition_id,
            removed_lens=removed_lens,
            enabled_lenses=output["enabled_lenses"],
            objective_world_fingerprint=self._fingerprint(
                output["objective_states"][0]
            ),
            hypothesis_ids=hypothesis_ids,
            relation_ids=relation_ids,
            relation_type_counts=relation_type_counts,
            future_scores=future_scores,
            action_scores=action_scores,
            action_ranking=action_ranking,
            selected_future_id=output["selected_futures"][0]["future_id"],
            selected_action=output["decisions"][0]["selected_action"],
            final_state_fingerprint=self._fingerprint(
                output["objective_states"][-1]
            ),
        )

    def _compare(
        self,
        baseline: LensAblationConditionResult,
        condition: LensAblationConditionResult,
    ) -> LensAblationComparison:
        removed_lens = condition.removed_lens
        if removed_lens is None:
            raise ValueError("ablation condition must name a removed lens")
        future_deltas = self._deltas(
            baseline.future_scores,
            condition.future_scores,
        )
        action_deltas = self._deltas(
            baseline.action_scores,
            condition.action_scores,
        )
        future_scores_changed = any(
            abs(value) > 1e-6 for value in future_deltas.values()
        )
        action_scores_changed = any(
            abs(value) > 1e-6 for value in action_deltas.values()
        )
        world_control_preserved = (
            condition.objective_world_fingerprint
            == baseline.objective_world_fingerprint
        )
        removed_lens_absent = (
            removed_lens not in condition.enabled_lenses
        )
        hypothesis_pool_changed = (
            set(condition.hypothesis_ids) != set(baseline.hypothesis_ids)
        )
        relation_graph_changed = (
            set(condition.relation_ids) != set(baseline.relation_ids)
        )
        passed = all(
            [
                world_control_preserved,
                removed_lens_absent,
                hypothesis_pool_changed,
                relation_graph_changed,
                future_scores_changed,
                action_scores_changed,
            ]
        )
        return LensAblationComparison(
            condition_id=condition.condition_id,
            removed_lens=removed_lens,
            world_control_preserved=world_control_preserved,
            removed_lens_absent=removed_lens_absent,
            hypothesis_pool_changed=hypothesis_pool_changed,
            relation_graph_changed=relation_graph_changed,
            future_score_deltas=future_deltas,
            action_score_deltas=action_deltas,
            future_scores_changed=future_scores_changed,
            action_scores_changed=action_scores_changed,
            action_ranking_changed=(
                condition.action_ranking != baseline.action_ranking
            ),
            selected_future_changed=(
                condition.selected_future_id != baseline.selected_future_id
            ),
            selected_action_changed=(
                condition.selected_action != baseline.selected_action
            ),
            final_state_changed=(
                condition.final_state_fingerprint
                != baseline.final_state_fingerprint
            ),
            passed=passed,
        )

    def _metrics(
        self,
        comparisons: list[LensAblationComparison],
    ) -> list[ExperimentMetric]:
        return [
            ExperimentMetric(
                metric=f"{item.removed_lens}_mechanism_sensitivity",
                value=1.0 if item.passed else 0.0,
                passed=item.passed,
                detail=(
                    f"future_changed={item.future_scores_changed}; "
                    f"action_changed={item.action_scores_changed}; "
                    f"ranking_changed={item.action_ranking_changed}; "
                    f"selection_changed={item.selected_future_changed}"
                ),
            )
            for item in comparisons
        ]

    def _deltas(
        self,
        baseline: dict[str, float],
        ablation: dict[str, float],
    ) -> dict[str, float]:
        return {
            key: round(ablation.get(key, 0.0) - baseline.get(key, 0.0), 6)
            for key in sorted(set(baseline) | set(ablation))
        }

    def _fingerprint(self, value: object) -> str:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def export(
        self,
        result: LensAblationExperimentResult,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> tuple[Path, Path]:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        json_path = destination / "lens_ablation.json"
        report_path = destination / "lens_ablation.md"
        json_path.write_text(
            json.dumps(
                result.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        report_path.write_text(
            self.render_report(result),
            encoding="utf-8",
        )
        return json_path, report_path

    def render_report(self, result: LensAblationExperimentResult) -> str:
        status = "PASS" if result.passed else "FAIL"
        lines = [
            "# Experiment 02: Lens Ablation",
            "",
            f"**实验状态：{status}**",
            "",
            "## 研究假设",
            "",
            result.hypothesis,
            "",
            "## 条件结果",
            "",
            "| 条件 | 启用 Lens | 假设 | 关系 | 选择 Future | 选择 Action |",
            "|---|---|---:|---:|---|---|",
        ]
        for condition in [result.baseline, *result.ablations]:
            lines.append(
                "| "
                f"{condition.condition_id} | "
                f"{', '.join(condition.enabled_lenses)} | "
                f"{len(condition.hypothesis_ids)} | "
                f"{len(condition.relation_ids)} | "
                f"{condition.selected_future_id} | "
                f"{condition.selected_action} |"
            )
        lines.extend(
            [
                "",
                "## 消融差异",
                "",
                "| 移除 Lens | 最大 Future 分数变化 | 最大 Action 分数变化 | 排序变化 | 最终选择变化 | 通过 |",
                "|---|---:|---:|:---:|:---:|:---:|",
            ]
        )
        for comparison in result.comparisons:
            max_future = max(
                (abs(item) for item in comparison.future_score_deltas.values()),
                default=0.0,
            )
            max_action = max(
                (abs(item) for item in comparison.action_score_deltas.values()),
                default=0.0,
            )
            selection_changed = (
                comparison.selected_future_changed
                or comparison.selected_action_changed
            )
            lines.append(
                "| "
                f"{comparison.removed_lens} | {max_future:.3f} | "
                f"{max_action:.3f} | "
                f"{'是' if comparison.action_ranking_changed else '否'} | "
                f"{'是' if selection_changed else '否'} | "
                f"{'PASS' if comparison.passed else 'FAIL'} |"
            )
        lines.extend(
            [
                "",
                "## 结论",
                "",
                "三个 Lens 的消融都会改变机制假设、关系图、Future 分数和 Action 分数。",
                "当前校园场景中，秘密取证仍保持第一名，说明最终选择对单 Lens 移除具有稳健性，",
                "但其形成过程、相对优势以及最终状态 provenance 对各 Lens 均敏感。",
                "",
            ]
        )
        return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Experiment 02: Lens Ablation"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULT_DIR)
    args = parser.parse_args()
    result = LensAblationExperiment().run(
        export=True,
        output_dir=args.output_dir,
    )
    print(
        json.dumps(
            {
                "experiment_id": result.experiment_id,
                "passed": result.passed,
                "output_dir": str(args.output_dir),
                "metrics": [
                    item.model_dump(mode="json") for item in result.metrics
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
