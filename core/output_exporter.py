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
        state_provenance,
        agents,
        observations,
        evidence,
        belief_updates,
        belief_states,
        subjective_models,
        mental_models,
        bias_filter_results,
        interpretations,
        perceptions,
        emotional_appraisals,
        stress_states,
        motivation_states,
        information_boundaries,
        possible_worlds,
        world_evidence_assessments,
        prior_belief_distributions,
        world_revisions,
        posterior_belief_distributions,
        possible_world_beliefs,
        scarcity_assessments,
        information_asymmetries,
        incentive_assessments,
        opportunity_costs,
        economic_action_evaluations,
        role_assessments,
        norm_pressures,
        institution_powers,
        social_action_evaluations,
        beliefs_about_others,
        hypotheses,
        hypothesis_relations,
        candidate_futures,
        agent_action_decisions,
        future_evaluations,
        selected_futures,
        value_assessments,
        decisions,
        actions,
        world_events,
        narrative_events,
        scene_cards,
        image_prompts,
    ) -> Path:
        run_dir = self._next_run_dir()
        run_dir.mkdir(parents=True, exist_ok=False)

        self._write_json(run_dir / "objective_states.json", objective_states)
        self._write_json(run_dir / "state_provenance.json", state_provenance)
        self._write_json(run_dir / "agent_profiles.json", agents)
        self._write_json(run_dir / "observations.json", observations)
        self._write_json(run_dir / "evidence.json", evidence)
        self._write_json(run_dir / "belief_updates.json", belief_updates)
        self._write_json(run_dir / "belief_states.json", belief_states)
        self._write_json(run_dir / "subjective_models.json", subjective_models)
        self._write_json(run_dir / "mental_models.json", mental_models)
        self._write_json(run_dir / "bias_filter_results.json", bias_filter_results)
        self._write_json(run_dir / "interpretations.json", interpretations)
        self._write_json(run_dir / "perceptions.json", perceptions)
        self._write_json(
            run_dir / "emotional_appraisals.json",
            emotional_appraisals,
        )
        self._write_json(run_dir / "stress_states.json", stress_states)
        self._write_json(run_dir / "motivation_states.json", motivation_states)
        self._write_json(
            run_dir / "information_boundaries.json",
            information_boundaries,
        )
        self._write_json(run_dir / "possible_worlds.json", possible_worlds)
        self._write_json(
            run_dir / "world_evidence_assessments.json",
            world_evidence_assessments,
        )
        self._write_json(
            run_dir / "prior_belief_distributions.json",
            prior_belief_distributions,
        )
        self._write_json(run_dir / "world_revisions.json", world_revisions)
        self._write_json(
            run_dir / "posterior_belief_distributions.json",
            posterior_belief_distributions,
        )
        self._write_json(
            run_dir / "possible_world_beliefs.json",
            possible_world_beliefs,
        )
        self._write_json(
            run_dir / "scarcity_assessments.json",
            scarcity_assessments,
        )
        self._write_json(
            run_dir / "information_asymmetries.json",
            information_asymmetries,
        )
        self._write_json(
            run_dir / "incentive_assessments.json",
            incentive_assessments,
        )
        self._write_json(run_dir / "opportunity_costs.json", opportunity_costs)
        self._write_json(
            run_dir / "economic_action_evaluations.json",
            economic_action_evaluations,
        )
        self._write_json(run_dir / "role_assessments.json", role_assessments)
        self._write_json(run_dir / "norm_pressures.json", norm_pressures)
        self._write_json(
            run_dir / "institution_powers.json",
            institution_powers,
        )
        self._write_json(
            run_dir / "social_action_evaluations.json",
            social_action_evaluations,
        )
        self._write_json(run_dir / "beliefs_about_others.json", beliefs_about_others)
        self._write_json(run_dir / "hypotheses.json", hypotheses)
        self._write_json(
            run_dir / "hypothesis_relations.json",
            hypothesis_relations,
        )
        self._write_json(run_dir / "candidate_futures.json", candidate_futures)
        self._write_json(
            run_dir / "agent_action_decisions.json",
            agent_action_decisions,
        )
        self._write_json(
            run_dir / "future_evaluations.json",
            future_evaluations,
        )
        self._write_json(run_dir / "selected_futures.json", selected_futures)
        self._write_json(run_dir / "value_assessments.json", value_assessments)
        self._write_json(run_dir / "decisions.json", decisions)
        self._write_json(run_dir / "actions.json", actions)
        self._write_json(run_dir / "world_events.json", world_events)
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
