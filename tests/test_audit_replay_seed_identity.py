from __future__ import annotations

import unittest

from shadowseed_agent_lab.audit_replay import replay_session
from shadowseed_agent_lab.session_runner import GateEvent, SessionDecision, SessionResult, SessionSeed


class AuditReplaySeedIdentityTests(unittest.TestCase):
    def test_allowed_decision_must_match_session_seed(self) -> None:
        result = SessionResult(
            input_id="case",
            seed_before_gate=SessionSeed("owner_missing", 1.0, 0.0, "NEW"),
            seed_after_gate=SessionSeed("owner_missing", 1.0, 0.6, "PROMOTED"),
            evidence_refs=(),
            verified_evidence_refs=(),
            gate_event=GateEvent("owner_missing", True, "PROMOTED", 0.6, ("ref",), "ok", "fixture"),
            probe_suggestion=None,
            decisions=(SessionDecision("deadline_missing", "probe", True, "ok", "gate:owner_missing"),),
        )

        report = replay_session(result)

        self.assertFalse(report.ok)
        self.assertEqual(report.findings[0].reason, "decision_seed_mismatch")

    def test_allowed_decision_must_match_gate_seed(self) -> None:
        result = SessionResult(
            input_id="case",
            seed_before_gate=SessionSeed("owner_missing", 1.0, 0.0, "NEW"),
            seed_after_gate=SessionSeed("owner_missing", 1.0, 0.6, "PROMOTED"),
            evidence_refs=(),
            verified_evidence_refs=(),
            gate_event=GateEvent("deadline_missing", True, "PROMOTED", 0.6, ("ref",), "ok", "fixture"),
            probe_suggestion=None,
            decisions=(SessionDecision("owner_missing", "probe", True, "ok", "gate:owner_missing"),),
        )

        report = replay_session(result)

        self.assertFalse(report.ok)
        self.assertEqual(report.findings[0].reason, "gate_seed_mismatch")


if __name__ == "__main__":
    unittest.main()
