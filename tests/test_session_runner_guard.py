from __future__ import annotations

import unittest

from shadowseed_agent_lab import AgentSessionRunner, FixtureEvidenceAdapter, SessionRequest


class SessionRunnerGuardTests(unittest.TestCase):
    def test_candidate_text_is_required(self) -> None:
        runner = AgentSessionRunner(FixtureEvidenceAdapter([]))
        candidate = "owner_missing".replace("owner_missing", "")

        with self.assertRaises(ValueError):
            runner.run(SessionRequest("case", "input text", candidate))

    def test_candidate_text_must_have_content(self) -> None:
        runner = AgentSessionRunner(FixtureEvidenceAdapter([]))
        candidate = chr(32) * 3

        with self.assertRaises(ValueError):
            runner.run(SessionRequest("case", "input text", candidate))


if __name__ == "__main__":
    unittest.main()
