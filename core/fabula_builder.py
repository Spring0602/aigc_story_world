from schemas import Fabula, FabulaEvent, ObjectiveWorldState, StateProvenance


class FabulaBuilder:
    def build(
        self,
        states: list[ObjectiveWorldState],
        provenance: list[StateProvenance],
    ) -> Fabula:
        if len(states) < 2:
            raise ValueError("fabula requires at least one world transition")
        provenance_by_event: dict[str, list[StateProvenance]] = {}
        for item in provenance:
            if item.event_id:
                provenance_by_event.setdefault(item.event_id, []).append(item)

        events = []
        for index, target_state in enumerate(states[1:], start=1):
            source_state = states[index - 1]
            source_event_ids = {item.event_id for item in source_state.events}
            new_events = [
                item
                for item in target_state.events
                if item.event_id not in source_event_ids
            ]
            for event in new_events:
                event_provenance = provenance_by_event.get(event.event_id, [])
                events.append(
                    FabulaEvent(
                        fabula_event_id=f"fabula_{event.event_id}",
                        world_event_id=event.event_id,
                        step=target_state.step,
                        timestamp=event.timestamp,
                        source_state_id=source_state.state_id,
                        target_state_id=target_state.state_id,
                        summary=event.description,
                        visibility=event.visibility,
                        actor_ids=event.actor_ids,
                        action_ids=event.action_ids,
                        decision_ids=event.decision_ids,
                        cause_ids=event.cause_ids,
                        effect_paths=event.effect_paths,
                        provenance_ids=event.provenance_ids,
                        source_observation_ids=event.source_observation_ids,
                        source_belief_ids=event.source_belief_ids,
                    )
                )
        chronology_valid = all(
            events[index - 1].step <= item.step
            and events[index - 1].target_state_id == item.source_state_id
            for index, item in enumerate(events[1:], start=1)
        )
        causality_preserved = all(
            item.provenance_ids
            and set(item.provenance_ids)
            == {
                record.provenance_id
                for record in provenance_by_event.get(item.world_event_id, [])
            }
            for item in events
        )
        return Fabula(
            fabula_id=f"fabula_{states[0].state_id}_{states[-1].state_id}",
            initial_state_id=states[0].state_id,
            final_state_id=states[-1].state_id,
            state_ids=[item.state_id for item in states],
            events=events,
            chronology_valid=chronology_valid,
            causality_preserved=causality_preserved,
        )
