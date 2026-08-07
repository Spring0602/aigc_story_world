from typing import Any

from pydantic import BaseModel

from schemas import (
    CandidateFuture,
    Event,
    FabulaEvent,
    FutureEvaluation,
    NarrativeImportanceAssessment,
    NarrativeImportanceBreakdown,
    ObjectiveWorldState,
    SubjectiveWorldModel,
)


class NarrativeImportance:
    MECHANISM_SCORES = {
        "conflict_change": {
            "information_discovery": 0.30,
            "social_coordination": 0.35,
            "institutional_contestation": 0.80,
            "process_inertia": 0.10,
        },
        "information_gain": {
            "information_discovery": 0.90,
            "social_coordination": 0.45,
            "institutional_contestation": 0.65,
            "process_inertia": 0.20,
        },
        "visual_potential": {
            "information_discovery": 0.90,
            "social_coordination": 0.70,
            "institutional_contestation": 0.80,
            "process_inertia": 0.35,
        },
    }

    def assess(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        event: Event,
        future: CandidateFuture,
        subjective_models: list[SubjectiveWorldModel],
        future_evaluation: FutureEvaluation | None = None,
        fabula_event: FabulaEvent | None = None,
    ) -> NarrativeImportanceAssessment:
        self._validate_sources(old_state, new_state, event, future)
        if fabula_event and fabula_event.world_event_id != event.event_id:
            raise ValueError("fabula event does not reference the source world event")
        dimensions = {
            "conflict_change": self._conflict_change(
                old_state,
                new_state,
                future,
            ),
            "information_gain": self._information_gain(event, future),
            "character_decision": self._character_decision(
                event,
                future,
                subjective_models,
            ),
            "relationship_change": self._relationship_change(
                old_state,
                new_state,
                future,
            ),
            "irreversibility": self._irreversibility(future),
            "theme_relevance": self._theme_relevance(
                future,
                subjective_models,
                future_evaluation,
            ),
            "visual_potential": self._visual_potential(event, future),
        }
        weighted_score = self._weighted_score(dimensions)
        breakdown = NarrativeImportanceBreakdown(
            **dimensions,
            weighted_score=weighted_score,
        )
        band = (
            "high"
            if weighted_score >= 0.7
            else "medium" if weighted_score >= 0.4 else "low"
        )
        mechanism = self._mechanism_type(future)
        return NarrativeImportanceAssessment(
            assessment_id=f"narrative_importance_{event.event_id}",
            step=new_state.step,
            source_event_id=event.event_id,
            source_fabula_event_id=(
                fabula_event.fabula_event_id if fabula_event else None
            ),
            source_future_id=future.future_id,
            source_future_evaluation_id=(
                future_evaluation.evaluation_id
                if future_evaluation
                else None
            ),
            source_state_id=old_state.state_id,
            target_state_id=new_state.state_id,
            importance_band=band,
            score_breakdown=breakdown,
            action_ids=list(event.action_ids),
            decision_ids=list(event.decision_ids),
            provenance_ids=list(event.provenance_ids),
            state_change_paths=list(event.effect_paths),
            dimension_rationales=self._rationales(mechanism, event, future),
            rationale=(
                f"The {mechanism} event has {band} narrative importance; "
                "the score is derived from world change and causal provenance, "
                "not from dramatic wording."
            ),
        )

    def score(self, future: CandidateFuture) -> float:
        """Compatibility entry point when only a candidate future is available."""
        mechanism = self._mechanism_type(future)
        values = {
            "conflict_change": self._mechanism_score(
                "conflict_change",
                mechanism,
            ),
            "information_gain": self._mechanism_score(
                "information_gain",
                mechanism,
            ),
            "character_decision": self._clamp(
                0.35
                + future.bounded_rationality_score * 0.45
                + (0.2 if future.agent_actions else 0.0)
            ),
            "relationship_change": (
                0.9
                if self._has_path(future, "relationships.")
                else 0.55 if mechanism == "social_coordination" else 0.1
            ),
            "irreversibility": self._irreversibility(future),
            "theme_relevance": self._clamp(
                0.25
                + min(0.3, len(future.supporting_hypotheses) * 0.08)
                + (
                    min(0.24, len(future.mechanism.lens_names) * 0.08)
                    if future.mechanism
                    else 0.0
                )
            ),
            "visual_potential": self._mechanism_score(
                "visual_potential",
                mechanism,
            ),
        }
        return self._weighted_score(values)

    def rank(
        self,
        assessments: list[NarrativeImportanceAssessment],
    ) -> list[NarrativeImportanceAssessment]:
        return sorted(
            assessments,
            key=lambda item: (
                -item.score_breakdown.weighted_score,
                item.source_event_id,
            ),
        )

    def _validate_sources(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        event: Event,
        future: CandidateFuture,
    ) -> None:
        if future.source_state_id != old_state.state_id:
            raise ValueError("narrative source future does not match old state")
        if event.event_id not in {item.event_id for item in new_state.events}:
            raise ValueError("narrative source event is absent from target state")
        if set(event.effect_paths) != {
            item.path for item in future.expected_state_changes
        }:
            raise ValueError("event effects do not match candidate future changes")

    def _conflict_change(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        future: CandidateFuture,
    ) -> float:
        score = self._mechanism_score(
            "conflict_change",
            self._mechanism_type(future),
        )
        for change in future.expected_state_changes:
            if change.path.startswith("institutions."):
                score = max(score, 0.75)
            if not change.path.startswith("relationships."):
                continue
            old_value = self._read_path(old_state, change.path)
            new_value = self._read_path(new_state, change.path)
            delta = self._numeric_delta(old_value, new_value)
            base = 0.6 if change.path.endswith(".conflict") else 0.45
            score = max(score, base + delta * 2)
        score += min(0.1, len(future.opposing_hypotheses) * 0.04)
        return self._clamp(score)

    def _information_gain(
        self,
        event: Event,
        future: CandidateFuture,
    ) -> float:
        score = self._mechanism_score(
            "information_gain",
            self._mechanism_type(future),
        )
        if any(
            path.startswith(("public_information.", "hidden_facts."))
            for path in event.effect_paths
        ):
            return 1.0
        if event.source_observation_ids:
            score += min(0.08, len(event.source_observation_ids) * 0.04)
        return self._clamp(score)

    def _character_decision(
        self,
        event: Event,
        future: CandidateFuture,
        models: list[SubjectiveWorldModel],
    ) -> float:
        actors = set(event.actor_ids)
        has_goals_or_values = any(
            item.agent_id in actors and (item.goals or item.values)
            for item in models
        )
        return self._clamp(
            future.bounded_rationality_score * 0.45
            + (0.2 if event.action_ids else 0.0)
            + (0.2 if event.decision_ids else 0.0)
            + (0.15 if has_goals_or_values else 0.0)
        )

    def _relationship_change(
        self,
        old_state: ObjectiveWorldState,
        new_state: ObjectiveWorldState,
        future: CandidateFuture,
    ) -> float:
        scores = []
        for change in future.expected_state_changes:
            if change.path.startswith("relationships."):
                delta = self._numeric_delta(
                    self._read_path(old_state, change.path),
                    self._read_path(new_state, change.path),
                )
                scores.append(self._clamp(0.6 + delta * 4))
        if scores:
            return max(scores)
        return 0.55 if self._mechanism_type(future) == "social_coordination" else 0.1

    def _irreversibility(self, future: CandidateFuture) -> float:
        scores = []
        for change in future.expected_state_changes:
            path = change.path
            if path.startswith("resources."):
                scores.append(0.9)
            elif path.startswith(("public_information.", "hidden_facts.")):
                scores.append(0.85)
            elif path.startswith("active_processes."):
                scores.append(0.8)
            elif path.startswith("institutions."):
                scores.append(0.7)
            elif path.startswith("relationships."):
                scores.append(0.55)
            elif path.endswith(".location_id"):
                scores.append(0.3)
            elif path.endswith(".status"):
                scores.append(0.25)
            else:
                scores.append(0.4)
        return max(scores, default=0.1)

    def _theme_relevance(
        self,
        future: CandidateFuture,
        models: list[SubjectiveWorldModel],
        evaluation: FutureEvaluation | None,
    ) -> float:
        support = (
            evaluation.score_breakdown.causal_support
            if evaluation
            else future.estimated_plausibility
        )
        lens_count = len(future.mechanism.lens_names) if future.mechanism else 0
        actor_ids = {item.agent_id for item in future.agent_actions}
        character_theme = any(
            item.agent_id in actor_ids and (item.values or item.goals)
            for item in models
        )
        return self._clamp(
            0.2
            + support * 0.35
            + min(0.24, lens_count * 0.08)
            + min(0.12, len(future.supporting_hypotheses) * 0.04)
            + (0.09 if character_theme else 0.0)
        )

    def _visual_potential(
        self,
        event: Event,
        future: CandidateFuture,
    ) -> float:
        mechanism = self._mechanism_score(
            "visual_potential",
            self._mechanism_type(future),
        )
        return self._clamp(
            mechanism * 0.55
            + (0.15 if event.actor_ids else 0.0)
            + (0.15 if event.action_ids else 0.0)
            + (0.15 if event.effect_paths else 0.0)
        )

    def _rationales(
        self,
        mechanism: str,
        event: Event,
        future: CandidateFuture,
    ) -> dict[str, str]:
        return {
            "conflict_change": f"Uses {mechanism}, opposition, and social deltas.",
            "information_gain": "Uses information mechanism and observation provenance.",
            "character_decision": (
                f"Uses {len(event.decision_ids)} decisions, "
                f"{len(event.action_ids)} actions, and bounded rationality."
            ),
            "relationship_change": "Uses relationship paths or social coordination.",
            "irreversibility": "Uses the semantic class of validated change paths.",
            "theme_relevance": (
                f"Uses {len(future.supporting_hypotheses)} hypotheses, lenses, "
                "and actor values/goals."
            ),
            "visual_potential": "Uses concrete actors, actions, effects, and mechanism.",
        }

    def _weighted_score(self, values: dict[str, float]) -> float:
        return round(
            sum(
                values[field] * weight
                for field, weight in NarrativeImportanceBreakdown.weights.items()
            ),
            3,
        )

    def _mechanism_type(self, future: CandidateFuture) -> str:
        return future.mechanism.mechanism_type if future.mechanism else "unspecified"

    def _mechanism_score(self, dimension: str, mechanism: str) -> float:
        defaults = {
            "conflict_change": 0.2,
            "information_gain": 0.3,
            "visual_potential": 0.45,
        }
        return self.MECHANISM_SCORES[dimension].get(
            mechanism,
            defaults[dimension],
        )

    def _has_path(self, future: CandidateFuture, prefix: str) -> bool:
        return any(
            item.path.startswith(prefix)
            for item in future.expected_state_changes
        )

    def _read_path(self, state: ObjectiveWorldState, path: str) -> Any:
        current: Any = state
        for part in path.split("."):
            if isinstance(current, BaseModel):
                current = getattr(current, part)
            elif isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
        return current

    def _numeric_delta(self, old_value: Any, new_value: Any) -> float:
        if isinstance(old_value, (int, float)) and isinstance(
            new_value,
            (int, float),
        ):
            return abs(float(new_value) - float(old_value))
        return 0.1

    def _clamp(self, value: float) -> float:
        return round(min(1.0, max(0.0, value)), 3)
