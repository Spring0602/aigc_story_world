import json
from pathlib import Path

from config import OUTPUT_DIR
from core.model_utils import to_dict


class OutputExporter:
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = Path(output_dir)

    def export_all(
        self,
        objective_states,
        agents,
        observations,
        subjective_models,
        mental_models,
        bias_filter_results,
        interpretations,
        hypotheses,
        candidate_futures,
        selected_futures,
        narrative_events,
        scene_cards,
        image_prompts,
    ) -> Path:
        run_dir = self._next_run_dir()
        run_dir.mkdir(parents=True, exist_ok=False)

        self._write_json(run_dir / "objective_states.json", objective_states)
        self._write_json(run_dir / "agent_profiles.json", agents)
        self._write_json(run_dir / "observations.json", observations)
        self._write_json(run_dir / "subjective_models.json", subjective_models)
        self._write_json(run_dir / "mental_models.json", mental_models)
        self._write_json(run_dir / "bias_filter_results.json", bias_filter_results)
        self._write_json(run_dir / "interpretations.json", interpretations)
        self._write_json(run_dir / "hypotheses.json", hypotheses)
        self._write_json(run_dir / "candidate_futures.json", candidate_futures)
        self._write_json(run_dir / "selected_futures.json", selected_futures)
        self._write_json(run_dir / "narrative_events.json", narrative_events)
        self._write_json(run_dir / "scene_cards.json", scene_cards)
        self._write_json(run_dir / "image_prompts.json", image_prompts)
        (run_dir / "report.md").write_text(self._build_report(selected_futures, narrative_events), encoding="utf-8")
        return run_dir

    def _next_run_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        existing = [
            int(path.name.removeprefix("run_"))
            for path in self.output_dir.glob("run_*")
            if path.is_dir() and path.name.removeprefix("run_").isdigit()
        ]
        next_index = max(existing, default=0) + 1
        return self.output_dir / f"run_{next_index:03d}"

    def _write_json(self, path: Path, data) -> None:
        path.write_text(json.dumps(to_dict(data), ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_report(self, selected_futures, narrative_events) -> str:
        lines = ["# StoryWorld V2 Run Report", ""]
        for future, event in zip(selected_futures, narrative_events):
            lines.extend(
                [
                    f"## {future.future_id}",
                    "",
                    f"- Selected future: {future.summary}",
                    f"- Plausibility: {future.estimated_plausibility}",
                    f"- Narrative event: {event.summary}",
                    "",
                ]
            )
        return "\n".join(lines)
