import unittest

from core.observation_engine import ObservationEngine
from core.world_initializer import WorldInitializer
from schemas import InformationItem


class ObservationTest(unittest.TestCase):
    def test_hidden_facts_are_not_public_observations(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        observations = ObservationEngine().observe(state, models)

        observations_by_agent = {
            agent_id: [item for item in observations if item.agent_id == agent_id]
            for agent_id in state.agents
        }
        all_information_ids = {item.information_id for item in observations}

        self.assertNotIn("info_hidden_scope_unclear", all_information_ids)
        self.assertIn("info_public_network_upgrade", all_information_ids)
        self.assertIn("info_private_dns_redirect", {item.information_id for item in observations_by_agent["lin_xia"]})
        self.assertNotIn("info_private_dns_redirect", {item.information_id for item in observations_by_agent["wang_chen"]})

    def test_role_information_requires_an_allowed_role(self):
        state, agents, models = WorldInitializer().initialize("校园监控")
        state.hidden_facts.append(
            InformationItem(
                info_id="info_student_channel",
                content="Student-only channel notice",
                visibility="role",
                source="student_union",
                evidence_type="social_consensus",
                allowed_roles=["student"],
            )
        )

        observations = ObservationEngine().observe(state, models)
        recipients = {
            item.agent_id for item in observations if item.information_id == "info_student_channel"
        }

        self.assertEqual(recipients, {"lin_xia", "wang_chen"})


if __name__ == "__main__":
    unittest.main()
