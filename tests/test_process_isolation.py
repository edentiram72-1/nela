from __future__ import annotations

import unittest

from agents.process_isolation import IsolatedAgentProcessRunner, blocking_sleep


class ProcessIsolationTests(unittest.TestCase):
    def test_completes_short_process(self) -> None:
        result = IsolatedAgentProcessRunner(timeout_seconds=1.0).run(blocking_sleep, 0.01)

        self.assertTrue(result.success)
        self.assertFalse(result.timed_out)
        self.assertEqual(result.data["result"], "done")

    def test_timeout_terminates_process_after_revocation_hook(self) -> None:
        revoked = []
        runner = IsolatedAgentProcessRunner(timeout_seconds=0.01, before_terminate=lambda: revoked.append(True))

        result = runner.run(blocking_sleep, 2.0)

        self.assertFalse(result.success)
        self.assertTrue(result.timed_out)
        self.assertEqual(revoked, [True])


if __name__ == "__main__":
    unittest.main()
