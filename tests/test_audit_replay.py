from __future__ import annotations

import unittest

from shadowseed_agent_lab import FixtureEvidenceAdapter
from shadowseed_agent_lab.audit_replay import replay_session, replay_sessions
from shadowseed_agent_lab.session_runner import (
    AgentSessionRunner,
    GateEvent,
    SessionDecision,
    SessionRequest,
    SessionResult,
    SessionSeed,
)


class AuditReplayTests(unittest.TestCase):
    def test_replay_passes_blocked_session(self) -> None:
        runner = AgentSessionRunner(FixtureEvidenceAdapter([]))

        result = runner.run(SessionRequest("case", "input text", "owner_missing"))
        report = replay_session(result)

        self.assertTrue(report.ok)
        self.assertEqual(report.findings[0].reason, "ok")

    def test_replay_fails_allowed_weightless_decision(self) -> None:
        result = SessionResult(
            input_id="case",
            seed_before_gate=SessionSeed("owner_missing", 1.0, 0.0, "NEW"),
            seed_after_gate=SessionSeed("owner_missing", 1.0, 0.0, "BLOCKED"),
            evidence_refs=(),
            verified_evidence_refs=(),
            gate_event=GateEvent("owner_missing", False, "BLOCKED", 0.0, (), "missing", "fixture"),
            probe_suggestion=None,
            decisions=(SessionDecision("owner_missing", "probe", True, "bad", "gate:owner_missing"),),
        )

        report = replay_session(result)

        self.assertFalse(report.ok)
        self.assertEqual(report.findings[0].reason, "allowed_weightless_seed")

    def test_replay_fails_missing_gate_ref(self) -> None:
        result = SessionResult(
            input_id="case",
            seed_before_gate=SessionSeed("owner_missing", 1.0, 0.0, "NEW"),
            seed_after_gate=SessionSeed("owner_missing", 1.0, 0.6, "PROMOTED"),
            evidence_refs=(),
            verified_evidence_refs=(),
            gate_event=GateEvent("owner_missing", True, "PROMOTED", 0.6, ("ref",), "ok", "fixture"),
            probe_suggestion=None,
            decisions=(SessionDecision("owner_missing", "probe", True, "ok", None),),
        )

        report = replay_session(result)

        self.assertFalse(report.ok)
        self.assertEqual(report.findings[0].reason, "missing_gate_ref")

    def test_replay_sessions_combines_findings(self) -> None:
        runner = AgentSessionRunner(FixtureEvidenceAdapter([]))
        first = runner.run(SessionRequest("one", "input text", "owner_missing"))
        second = runner.run(SessionRequest("two", "input text", "deadline_missing"))

        report = replay_sessions([first, second])

        self.assertTrue(report.ok)
        self.assertEqual(len(report.findings), 2)


if __name__ == "__main__":
    unittest.main()
