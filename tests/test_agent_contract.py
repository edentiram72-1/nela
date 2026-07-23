import unittest

from agents.base import AgentCommand, AgentState
from agents.spotify.agent import SpotifyAgent


class AgentContractTests(unittest.TestCase):
    def test_agent_contract_lifecycle(self) -> None:
        agent = SpotifyAgent()

        self.assertEqual(agent.status(), AgentState.CREATED)
        self.assertTrue(agent.initialize().success)
        self.assertEqual(agent.status(), AgentState.READY)

        result = agent.execute(AgentCommand(action="play"))
        self.assertFalse(result.success)
        self.assertIn("not implemented", result.message)

        self.assertTrue(agent.health_check().success)
        self.assertTrue(agent.stop().success)
        self.assertEqual(agent.status(), AgentState.STOPPED)


if __name__ == "__main__":
    unittest.main()
