import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from app import run_pipeline
from schemas import MultiStepSimulationResult, SimulationStepTrace


DEFAULT_RESULT_DIR = Path(__file__).resolve().parent / "results"


class MultiStepSimulation:
    """Run and validate Day 29's bounded multi-step world rollout."""

    def run(
        self,
        *,
        steps: int = 3,
        export: bool = False,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> MultiStepSimulationResult:
        if not 3 <= steps <= 5:
            raise ValueError("multi-step simulation requires 3 to 5 steps")
        output = run_pipeline("校园监控", steps=steps, export=False)
        result = self._build_result(output, steps)
        if export:
            self.export(result, output_dir)
        return result

    def export(
        self,
        result: MultiStepSimulationResult,
        output_dir: str | Path = DEFAULT_RESULT_DIR,
    ) -> tuple[Path, Path]:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        json_path = destination / "multi_step_simulation.json"
        report_path = destination / "multi_step_simulation.md"
        json_path.write_text(
            json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        report_path.write_text(self._report(result), encoding="utf-8")
        return json_path, report_path

    def _build_result(
        self,
        output: dict[str, Any],
        steps: int,
    ) -> MultiStepSimulationResult:
        states = output["objective_states"]
        traces = [
            self._trace(output, index)
            for index in range(steps)
        ]
        continuity = all(
            trace.source_state_id == states[index]["state_id"]
            and trace.target_state_id == states[index + 1]["state_id"]
            and (
                index == 0
                or traces[index - 1].target_state_id
                == trace.source_state_id
            )
            for index, trace in enumerate(traces)
        )
        snapshots_immutable = all(
            trace.source_values_match and trace.target_values_match
            for trace in traces
        ) and len({self._fingerprint(item) for item in states}) == len(states)
        provenance_complete = all(
            trace.references_closed and trace.provenance_ids
            for trace in traces
        )
        no_noop_changes = all(
            self._step_has_no_noop(output, index)
            for index in range(steps)
        )
        passed = all(
            (
                continuity,
                snapshots_immutable,
                provenance_complete,
                no_noop_changes,
            )
        )
        return MultiStepSimulationResult(
            simulation_id="day29_multi_step_simulation",
            requested_steps=steps,
            initial_state_id=states[0]["state_id"],
            final_state_id=states[-1]["state_id"],
            traces=traces,
            state_ids=[item["state_id"] for item in states],
            continuity_preserved=continuity,
            snapshots_immutable=snapshots_immutable,
            provenance_complete=provenance_complete,
            no_noop_changes=no_noop_changes,
            passed=passed,
        )

    def _trace(
        self,
        output: dict[str, Any],
        index: int,
    ) -> SimulationStepTrace:
        step = index + 1
        source = output["objective_states"][index]
        target = output["objective_states"][step]
        future = output["selected_futures"][index]
        decision = output["decisions"][index]
        actions = [item for item in output["actions"] if item["step"] == step]
        events = [
            item
            for item in output["world_events"]
            if item["timestamp"] == target["timestamp"]
        ]
        provenance = [
            item
            for item in output["state_provenance"]
            if item["source"] == "world_transition"
            and item["source_state_id"] == source["state_id"]
            and item["target_state_id"] == target["state_id"]
        ]
        candidate_futures = [
            item
            for item in output["candidate_futures"]
            if item["source_state_id"] == source["state_id"]
        ]
        changes = future["expected_state_changes"]
        source_matches = all(
            self._read(source, item["path"]) == item["old_value"]
            for item in changes
        )
        target_matches = all(
            self._read(target, item["path"]) == item["new_value"]
            for item in changes
        )
        provenance_ids = {item["provenance_id"] for item in provenance}
        action_ids = {item["action_id"] for item in actions}
        event_ids = {item["event_id"] for item in events}
        references_closed = bool(provenance) and all(
            item["future_id"] == future["future_id"]
            and item["source_state_id"] == source["state_id"]
            and item["target_state_id"] == target["state_id"]
            and set(item["action_ids"]) == action_ids
            and item["event_id"] in event_ids
            and bool(item["decision_ids"])
            and bool(item["future_evaluation_id"])
            and bool(item["source_observation_ids"])
            and bool(item["supporting_belief_ids"])
            and bool(item["constraint_ids"])
            for item in provenance
        ) and all(
            set(item["provenance_ids"]) == provenance_ids
            for item in events
        )
        return SimulationStepTrace(
            step=step,
            source_state_id=source["state_id"],
            target_state_id=target["state_id"],
            selected_future_id=future["future_id"],
            selected_mechanism_type=future["mechanism"]["mechanism_type"],
            selected_action=decision["selected_action"],
            observation_ids=sorted(
                item["observation_id"]
                for item in output["observations"]
                if item["step"] == index
            ),
            belief_state_ids=sorted(
                item["belief_state_id"]
                for item in output["belief_states"]
                if item["step"] == index
            ),
            candidate_future_ids=sorted(
                item["future_id"] for item in candidate_futures
            ),
            decision_ids=[decision["decision_id"]],
            action_ids=sorted(action_ids),
            event_ids=sorted(event_ids),
            state_change_paths=[item["path"] for item in changes],
            provenance_ids=sorted(provenance_ids),
            source_values_match=source_matches,
            target_values_match=target_matches,
            references_closed=references_closed,
        )

    def _step_has_no_noop(self, output: dict[str, Any], index: int) -> bool:
        return all(
            item["old_value"] != item["new_value"]
            for item in output["selected_futures"][index][
                "expected_state_changes"
            ]
        )

    def _read(self, state: dict[str, Any], path: str) -> Any:
        current: Any = state
        for part in path.split("."):
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
        return current

    def _fingerprint(self, value: Any) -> str:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _report(self, result: MultiStepSimulationResult) -> str:
        lines = [
            "# Day 29 Multi-step Simulation",
            "",
            f"- Steps: {result.requested_steps}",
            f"- State chain: {' -> '.join(result.state_ids)}",
            f"- Continuity preserved: {result.continuity_preserved}",
            f"- Snapshots immutable: {result.snapshots_immutable}",
            f"- Provenance complete: {result.provenance_complete}",
            f"- No no-op changes: {result.no_noop_changes}",
            f"- Passed: {result.passed}",
            "",
            "## Trace",
            "",
        ]
        for trace in result.traces:
            lines.append(
                f"- Step {trace.step}: {trace.source_state_id} -> "
                f"{trace.target_state_id}; {trace.selected_action}; "
                f"{trace.selected_mechanism_type}"
            )
        return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Day 29 simulation")
    parser.add_argument("--steps", type=int, default=3, choices=range(3, 6))
    parser.add_argument("--output-dir", default=str(DEFAULT_RESULT_DIR))
    args = parser.parse_args()
    result = MultiStepSimulation().run(
        steps=args.steps,
        export=True,
        output_dir=args.output_dir,
    )
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
