"""Tests that the lab consumes upstream `shadowseed_agent` and cannot drift.

These tests fail if the lab ever re-implements upstream safety semantics
instead of importing them.
"""

from __future__ import annotations

import unittest

from shadowseed_agent.agent_contract import (
    GENERATED_EVIDENCE_KINDS,
    AgentSafetyContract,
    evidence_can_support_gate,
)
from shadowseed_agent.audit_policy import WeightlessInfluenceError

from shadowseed_agent_lab import (
    AgentSessionRunner,
    EvidenceRef,
    FixtureEvidenceAdapter,
    GateEvent,
    SessionDecision,
    SessionRequest,
    SessionResult,
    SessionSeed,
    assert_no_weightless_influence_in_sessions,
    filter_verified_evidence,
)
from shadowseed_agent_lab.evidence_adapter import GENERATED_KINDS


class UpstreamIntegrationTests(unittest.TestCase):
    def test_generated_kinds_is_the_upstream_set(self) -> None:
        # Identity, not just equality: the lab must re-export, not copy.
        self.assertIs(GENERATED_KINDS, GENERATED_EVIDENCE_KINDS)

    def test_filter_matches_upstream_evidence_discipline(self) -> None:
        refs = [
            EvidenceRef("a", "s", "fixture_note", "t", verified=True, supports_seed="x"),
            EvidenceRef("b", "s", "llm_output", "t", verified=True, supports_seed="x"),
            EvidenceRef("c", "s", "fixture_note", "t", verified=False, supports_seed="x"),
        ]

        kept = filter_verified_evidence(refs)

        self.assertEqual([r.id for r in kept], ["a"])
        for ref in refs:
            self.assertEqual(ref.can_support_gate(), evidence_can_support_gate(ref))

    def test_probe_reasons_come_from_upstream_contract(self) -> None:
        runner = AgentSessionRunner(
            FixtureEvidenceAdapter(
                [EvidenceRef("ev", "s", "fixture_note", "owner_missing", True, "owner_missing")]
            )
        )

        promoted = runner.run(SessionRequest("p", "no owner", "owner_missing"))
        blocked = runner.run(SessionRequest("b", "no deadline", "deadline_missing"))

        # These exact reason strings are produced by AgentSafetyContract.decide.
        contract = AgentSafetyContract()
        self.assertEqual(
            promoted.decisions[0].reason,
            contract.decide(
                promoted.seed_after_gate, "probe", gate_log=(promoted.gate_event,)
            ).reason,
        )
        self.assertEqual(promoted.decisions[0].reason, "allowed_promoted_gate_logged")
        self.assertEqual(blocked.decisions[0].reason, "weightless_seed")

    def test_upstream_audit_flags_weightless_influence(self) -> None:
        bad = SessionResult(
            input_id="case",
            seed_before_gate=SessionSeed("owner_missing", 1.0, 0.0, "NEW"),
            seed_after_gate=SessionSeed("owner_missing", 1.0, 0.0, "BLOCKED"),
            evidence_refs=(),
            verified_evidence_refs=(),
            gate_event=GateEvent("owner_missing", False, "BLOCKED", 0.0, (), "x", "fixture"),
            probe_suggestion=None,
            decisions=(SessionDecision("owner_missing", "probe", True, "forced", "gate:x"),),
        )

        with self.assertRaises(WeightlessInfluenceError):
            assert_no_weightless_influence_in_sessions([bad])


if __name__ == "__main__":
    unittest.main()
