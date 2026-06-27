from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import unittest

from shadowseed_agent_lab import (
    AgentSessionRunner,
    CandidateEvidenceRequest,
    EvidenceRef,
    FixtureEvidenceAdapter,
    SessionRequest,
    load_fixture_adapter,
)

CORPUS = Path("examples/agent_lab/fixtures/evidence_corpus.json")


@dataclass
class RecordingLookup:
    refs: list[EvidenceRef]
    seen_request: CandidateEvidenceRequest | None = None

    def lookup(self, request: CandidateEvidenceRequest) -> list[EvidenceRef]:
        self.seen_request = request
        return self.refs


class SessionRunnerTests(unittest.TestCase):
    def test_seed_stays_blocked_without_verified_support(self) -> None:
        runner = AgentSessionRunner(
            FixtureEvidenceAdapter(
                [
                    EvidenceRef(
                        id="draft-ref",
                        source="note.md#draft",
                        kind="fixture_note",
                        text="Owner may be absent.",
                        verified=False,
                        supports_seed="owner_missing",
                    )
                ]
            )
        )

        result = runner.run(
            SessionRequest("s1", "The note has an item without an owner.", "owner_missing")
        )

        self.assertEqual(result.seed_before_gate.weight, 0.0)
        self.assertEqual(result.seed_after_gate.weight, 0.0)
        self.assertEqual(result.seed_after_gate.status, "BLOCKED")
        self.assertFalse(result.gate_event.promoted)
        self.assertIsNone(result.probe_suggestion)
        self.assertEqual(result.decisions[0].reason, "weightless_seed")

    def test_lookup_receives_request_not_seed(self) -> None:
        lookup = RecordingLookup(
            refs=[
                EvidenceRef(
                    id="owner-ref",
                    source="note.md#owner",
                    kind="fixture_note",
                    text="Items require a named owner.",
                    verified=True,
                    supports_seed="owner_missing",
                )
            ]
        )
        runner = AgentSessionRunner(lookup)

        runner.run(SessionRequest("s2", "The item has no owner.", "owner_missing"))

        self.assertIsInstance(lookup.seen_request, CandidateEvidenceRequest)
        assert lookup.seen_request is not None
        self.assertEqual(lookup.seen_request.input_id, "s2")
        self.assertEqual(lookup.seen_request.candidate_absence, "owner_missing")
        self.assertFalse(hasattr(lookup.seen_request, "weight"))
        self.assertFalse(hasattr(lookup.seen_request, "status"))

    def test_promoted_gate_logged_seed_gets_probe_suggestion(self) -> None:
        runner = AgentSessionRunner(load_fixture_adapter(CORPUS))

        result = runner.run(SessionRequest("s3", "The item has no owner.", "owner_missing"))

        self.assertEqual(result.seed_before_gate.weight, 0.0)
        self.assertEqual(result.seed_after_gate.weight, 0.6)
        self.assertEqual(result.seed_after_gate.status, "PROMOTED")
        self.assertTrue(result.gate_event.promoted)
        self.assertEqual(result.gate_event.evidence_ids, ("evidence-owner-001",))
        self.assertIsNotNone(result.probe_suggestion)
        assert result.probe_suggestion is not None
        self.assertEqual(result.probe_suggestion.probe, "ask_for_owner_missing")
        self.assertTrue(result.probe_suggestion.suggestion_only)
        self.assertEqual(result.decisions[0].reason, "allowed_promoted_gate_logged")

    def test_unrelated_verified_ref_does_not_promote(self) -> None:
        runner = AgentSessionRunner(
            FixtureEvidenceAdapter(
                [
                    EvidenceRef(
                        id="deadline-ref",
                        source="note.md#deadline",
                        kind="fixture_note",
                        text="Items require a deadline.",
                        verified=True,
                        supports_seed="deadline_missing",
                    )
                ]
            )
        )

        result = runner.run(SessionRequest("s4", "The item has no owner.", "owner_missing"))

        self.assertEqual(result.verified_evidence_refs, ())
        self.assertFalse(result.gate_event.promoted)
        self.assertIsNone(result.probe_suggestion)

    def test_generated_kind_does_not_promote(self) -> None:
        runner = AgentSessionRunner(
            FixtureEvidenceAdapter(
                [
                    EvidenceRef(
                        id="machine-ref",
                        source="draft.md#machine",
                        kind="model_output",
                        text="Owner may be missing.",
                        verified=True,
                        supports_seed="owner_missing",
                    )
                ]
            )
        )

        result = runner.run(SessionRequest("s5", "The item has no owner.", "owner_missing"))

        self.assertEqual(result.verified_evidence_refs, ())
        self.assertFalse(result.gate_event.promoted)
        self.assertIsNone(result.probe_suggestion)

    def test_decision_log_is_present_for_every_session(self) -> None:
        runner = AgentSessionRunner(load_fixture_adapter(CORPUS))

        result = runner.run(
            SessionRequest("s6", "The note lacks an evaluation criterion.", "evaluation_criterion_missing")
        )

        self.assertEqual(len(result.decisions), 1)
        self.assertEqual(result.decisions[0].action, "probe")
        self.assertEqual(result.decisions[0].seed_id, "evaluation_criterion_missing")
        self.assertEqual(result.decisions[0].gate_event_ref, "gate:evaluation_criterion_missing")


if __name__ == "__main__":
    unittest.main()
