from itertools import combinations

from schemas import CausalHypothesis, HypothesisRelation


class HypothesisConflictResolver:
    def resolve(
        self,
        hypotheses: list[CausalHypothesis],
    ) -> list[HypothesisRelation]:
        relations = []
        for source, target in combinations(hypotheses, 2):
            if source.lens == target.lens:
                continue
            affected_agents = sorted(
                set(source.affected_agents).intersection(
                    target.affected_agents
                )
            )
            if not affected_agents:
                continue
            relations.append(
                self._relate(source, target, affected_agents)
            )
        return relations

    def _relate(
        self,
        source: CausalHypothesis,
        target: CausalHypothesis,
        affected_agents: list[str],
    ) -> HypothesisRelation:
        source_promotes = set(source.promotes_actions)
        source_inhibits = set(source.inhibits_actions)
        target_promotes = set(target.promotes_actions)
        target_inhibits = set(target.inhibits_actions)
        conflicts = sorted(
            source_promotes.intersection(target_inhibits)
            | source_inhibits.intersection(target_promotes)
        )
        agreements = sorted(
            source_promotes.intersection(target_promotes)
            | source_inhibits.intersection(target_inhibits)
        )
        shared_drivers = sorted(
            self._mechanism_names(source.drivers).intersection(
                self._mechanism_names(target.drivers)
            )
        )

        if conflicts:
            relation_type = "contradicts"
            basis = [f"opposed_action:{item}" for item in conflicts]
            resolution_status = "unresolved"
            signal = len(conflicts)
        elif agreements:
            relation_type = "supports"
            basis = [f"shared_action_effect:{item}" for item in agreements]
            resolution_status = "reinforcing"
            signal = len(agreements)
        else:
            relation_type = "conditions"
            basis = [
                *[
                    f"source_constraint:{item}"
                    for item in source.constraints
                ],
                *[
                    f"target_constraint:{item}"
                    for item in target.constraints
                ],
            ]
            resolution_status = "context_dependent"
            signal = 1

        confidence = (source.confidence + target.confidence) / 2.0
        strength = min(1.0, confidence * (0.7 + (0.1 * signal)))
        return HypothesisRelation(
            relation_id=(
                f"relation_{source.hypothesis_id}__{target.hypothesis_id}"
            ),
            source_hypothesis_id=source.hypothesis_id,
            target_hypothesis_id=target.hypothesis_id,
            source_lens=source.lens,
            target_lens=target.lens,
            relation_type=relation_type,
            basis=basis,
            shared_drivers=shared_drivers,
            affected_agents=affected_agents,
            strength=strength,
            resolution_status=resolution_status,
        )

    def _mechanism_names(self, values: list[str]) -> set[str]:
        return {item.split(":", 1)[0] for item in values}
