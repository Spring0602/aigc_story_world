import unittest

from core.observation_engine import ObservationEngine
from core.theory_of_mind import TheoryOfMindEngine
from core.world_initializer import WorldInitializer
from schemas import Belief, BeliefAboutOther, Event


class TheoryOfMindTest(unittest.TestCase):
    def test_public_behavior_produces_a_second_order_belief(self) -> None:
        state, _, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)

        updated_models, other_models = TheoryOfMindEngine().infer(state, observations, models)
        lin_about_wang = next(
            item
            for item in other_models
            if item.observer_agent_id == "lin_xia" and item.target_agent_id == "wang_chen"
        )
        updated_lin = next(item for item in updated_models if item.agent_id == "lin_xia")

        self.assertIsInstance(lin_about_wang, BeliefAboutOther)
        self.assertEqual(lin_about_wang.order, 2)
        self.assertIn("正常安全措施", lin_about_wang.attributed_beliefs[0].proposition)
        self.assertEqual(lin_about_wang.predicted_action, "discourage public confrontation")
        self.assertIn("event_wang_reassures_lin", lin_about_wang.evidence_event_ids)
        self.assertEqual(updated_lin.beliefs_about_others["wang_chen"], lin_about_wang)

    def test_target_private_state_and_hidden_events_cannot_leak_into_other_model(self) -> None:
        state, _, models = WorldInitializer().initialize("校园监控")
        state.events.append(
            Event(
                event_id="event_wang_private_doubt",
                event_type="private_thought",
                timestamp="day_1_22_40",
                description="王晨私下怀疑学校正在监控学生。",
                visibility="hidden",
                participant_ids=["wang_chen"],
                actor_ids=["wang_chen"],
            )
        )
        observations = ObservationEngine().observe(state, models)
        engine = TheoryOfMindEngine()

        _, baseline = engine.infer(state, observations, models)
        changed_models = [item.model_copy(deep=True) for item in models]
        changed_wang = next(item for item in changed_models if item.agent_id == "wang_chen")
        changed_wang.beliefs = [
            Belief(
                belief_id="private_belief_wang_monitoring",
                proposition="学校正在监控学生网络。",
                confidence=0.99,
                source="private_reasoning",
            )
        ]
        _, changed = engine.infer(state, observations, changed_models)

        baseline_lin = next(
            item
            for item in baseline
            if item.observer_agent_id == "lin_xia" and item.target_agent_id == "wang_chen"
        )
        changed_lin = next(
            item
            for item in changed
            if item.observer_agent_id == "lin_xia" and item.target_agent_id == "wang_chen"
        )
        self.assertEqual(baseline_lin, changed_lin)
        self.assertNotIn("event_wang_private_doubt", changed_lin.evidence_event_ids)


if __name__ == "__main__":
    unittest.main()
