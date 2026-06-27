from __future__ import annotations

import unittest

from shadowseed_agent_lab import FixtureEvidenceAdapter
from shadowseed_agent_lab.session_runner import AgentSessionRunner, GateEvent, SessionRequest, SessionSeed


class BlockingPolicy:
    def decide(self, seed: SessionSeed, verified_refs: tuple[object, ...]) -> GateEvent:
        return GateEvent(
            seed_id=seed.id,
            promoted=False,
            status_after="BLOCKED",
            weight_after=0.0,
            evidence_ids=(),
            reason="blocked_by_custom_policy",
            policy="custom_policy",
        )


class SessionRunnerPolicyTests(unittest.TestCase):
    def test_runner_uses_custom_policy(self) -> None:
        runner = AgentSessionRunner(FixtureEvidenceAdapter([]), gate_policy=BlockingPolicy())

        result = runner.run(SessionRequest("case", "input text", "owner_missing"))

        self.assertEqual(result.gate_event.policy, "custom_policy")
        self.assertEqual(result.seed_after_gate.weight, 0.0)
        self.assertIsNone(result.probe_suggestion)


if __name__ == "__main__":
    unittest.main()
