from schemas import (
    Fabula,
    Focalization,
    NarrativeEvent,
    NarrativeBeat,
    NarrativeImportanceAssessment,
    NarrativeImportanceBreakdown,
    NarrativePlan,
    NarrativePlanItem,
    ObjectiveWorldState,
    Observation,
    StoryOutput,
    Syuzhet,
)


class NarrativePlanner:
    def plan(
        self,
        fabula: Fabula,
        assessments: list[NarrativeImportanceAssessment],
        selection_threshold: float = 0.4,
    ) -> NarrativePlan:
        assessments_by_event = {
            item.source_fabula_event_id: item for item in assessments
        }
        selected = []
        omitted = []
        for event in fabula.events:
            assessment = assessments_by_event.get(event.fabula_event_id)
            if assessment is None:
                raise ValueError("every fabula event requires an importance assessment")
            if assessment.score_breakdown.weighted_score >= selection_threshold:
                selected.append(self._plan_item(event.fabula_event_id, assessment))
            else:
                omitted.append(event.fabula_event_id)
        if not selected:
            best = max(
                assessments,
                key=lambda item: item.score_breakdown.weighted_score,
            )
            selected.append(self._plan_item(best.source_fabula_event_id or "", best))
            omitted = [
                item.fabula_event_id
                for item in fabula.events
                if item.fabula_event_id != best.source_fabula_event_id
            ]
        return NarrativePlan(
            narrative_plan_id=f"narrative_plan_{fabula.fabula_id}",
            fabula_id=fabula.fabula_id,
            selection_threshold=selection_threshold,
            selected_items=selected,
            omitted_fabula_event_ids=omitted,
            planner_rationale=(
                "Select causally grounded fabula events at or above the "
                "importance threshold while preserving at least one event."
            ),
        )

    def arrange(self, fabula: Fabula, plan: NarrativePlan) -> Syuzhet:
        selected_ids = {
            item.fabula_event_id for item in plan.selected_items
        }
        ordered_ids = [
            item.fabula_event_id
            for item in fabula.events
            if item.fabula_event_id in selected_ids
        ]
        return Syuzhet(
            syuzhet_id=f"syuzhet_{fabula.fabula_id}",
            narrative_plan_id=plan.narrative_plan_id,
            arrangement="chronological",
            ordered_fabula_event_ids=ordered_ids,
            ordering_rationale=(
                "The first implementation preserves Fabula chronology; "
                "presentation order remains independently represented."
            ),
        )

    def focalize(
        self,
        fabula: Fabula,
        syuzhet: Syuzhet,
        state: ObjectiveWorldState,
        observations: list[Observation],
    ) -> list[Focalization]:
        events_by_id = {item.fabula_event_id: item for item in fabula.events}
        observations_by_id = {
            item.observation_id: item for item in observations
        }
        all_information_ids = {
            item.info_id
            for item in [*state.public_information, *state.hidden_facts]
        }
        results = []
        for event_id in syuzhet.ordered_fabula_event_ids:
            event = events_by_id[event_id]
            focal_agent = event.actor_ids[0] if event.actor_ids else sorted(state.agents)[0]
            visible_observations = [
                item
                for item in observations_by_id.values()
                if item.agent_id == focal_agent
                and item.step == event.step - 1
            ]
            known_ids = sorted(
                {item.information_id for item in visible_observations}
            )
            withheld_ids = sorted(all_information_ids - set(known_ids))
            results.append(
                Focalization(
                    focalization_id=f"focalization_{event.fabula_event_id}",
                    syuzhet_id=syuzhet.syuzhet_id,
                    fabula_event_id=event.fabula_event_id,
                    mode="third_person_limited",
                    focal_agent_id=focal_agent,
                    observation_ids=[
                        item.observation_id for item in visible_observations
                    ],
                    character_known_information_ids=known_ids,
                    audience_information_ids=known_ids,
                    withheld_information_ids=withheld_ids,
                    audience_knows_character_does_not=[],
                    character_knows_audience_does_not=[],
                    rationale=(
                        "Third-person limited narration exposes only information "
                        "supported by the focal agent's observations."
                    ),
                )
            )
        return results

    def story_output(
        self,
        fabula: Fabula,
        plan: NarrativePlan,
        syuzhet: Syuzhet,
        focalizations: list[Focalization],
        narrative_events: list[NarrativeEvent],
        narrative_beats: list[NarrativeBeat],
    ) -> StoryOutput:
        events_by_fabula = {
            item.source_fabula_event_id: item for item in narrative_events
        }
        ordered_events = [
            events_by_fabula[item]
            for item in syuzhet.ordered_fabula_event_ids
        ]
        beats_by_event = {
            item.narrative_event_id: item for item in narrative_beats
        }
        ordered_beats = [
            beats_by_event[item.narrative_event_id]
            for item in ordered_events
        ]
        return StoryOutput(
            story_output_id=f"story_output_{fabula.fabula_id}",
            fabula_id=fabula.fabula_id,
            narrative_plan_id=plan.narrative_plan_id,
            syuzhet_id=syuzhet.syuzhet_id,
            focalization_ids=[item.focalization_id for item in focalizations],
            narrative_event_ids=[
                item.narrative_event_id for item in ordered_events
            ],
            narrative_beat_ids=[
                item.narrative_beat_id for item in ordered_beats
            ],
            ordered_summaries=[item.summary for item in ordered_events],
            source_state_ids=list(fabula.state_ids),
            rendered_text="\n\n".join(
                item.rendered_text for item in ordered_beats
            ),
        )

    def _plan_item(
        self,
        fabula_event_id: str,
        assessment: NarrativeImportanceAssessment,
    ) -> NarrativePlanItem:
        dimensions = assessment.score_breakdown.model_dump(
            exclude={"weighted_score"}
        )
        dominant = max(
            dimensions,
            key=lambda item: (
                dimensions[item] * NarrativeImportanceBreakdown.weights[item]
            ),
        )
        functions = {
            "conflict_change": "confrontation",
            "information_gain": "revelation",
            "character_decision": "decision",
            "relationship_change": "relationship_shift",
            "irreversibility": "turning_point",
            "theme_relevance": "thematic_reinforcement",
            "visual_potential": "visual_emphasis",
        }
        return NarrativePlanItem(
            fabula_event_id=fabula_event_id,
            importance_assessment_id=assessment.assessment_id,
            importance_score=assessment.score_breakdown.weighted_score,
            narrative_function=functions[dominant],
            selection_reason=(
                f"Selected at {assessment.score_breakdown.weighted_score:.3f}; "
                f"dominant dimension is {dominant}."
            ),
        )
