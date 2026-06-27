from __future__ import annotations

from pathlib import Path
import unittest

from shadowseed_agent_lab import (
    CandidateEvidenceRequest,
    EvidenceRef,
    FixtureEvidenceAdapter,
    filter_verified_evidence,
    load_fixture_adapter,
)

CORPUS = Path("examples/agent_lab/fixtures/evidence_corpus.json")


class EvidenceAdapterTests(unittest.TestCase):
    def test_lookup_is_input_driven(self) -> None:
        adapter = load_fixture_adapter(CORPUS)
        request = CandidateEvidenceRequest(
            input_id="input-1",
            input_text="The project plan has an action point but no deadline.",
            candidate_absence="deadline_missing",
        )

        results = adapter.lookup(request)

        self.assertTrue(results)
        self.assertTrue(all(isinstance(ref, EvidenceRef) for ref in results))
        self.assertIn("evidence-deadline-001", {ref.id for ref in results})

    def test_weightless_seed_is_not_lookup_driver(self) -> None:
        adapter = load_fixture_adapter(CORPUS)

        with self.assertRaises(TypeError):
            adapter.lookup(  # type: ignore[arg-type]
                {
                    "seed_id": "deadline_missing",
                    "weight": 0.0,
                    "status": "NEW",
                }
            )

    def test_generated_output_is_not_verified_evidence(self) -> None:
        adapter = load_fixture_adapter(CORPUS)
        request = CandidateEvidenceRequest(
            input_id="input-2",
            input_text="The action point has no deadline.",
            candidate_absence="deadline_missing",
        )

        verified = filter_verified_evidence(adapter.lookup(request))

        self.assertNotIn("evidence-deadline-draft-001", {ref.id for ref in verified})
        self.assertTrue(all(ref.kind != "llm_output" for ref in verified))

    def test_verified_fixture_evidence_is_returned(self) -> None:
        adapter = load_fixture_adapter(CORPUS)
        request = CandidateEvidenceRequest(
            input_id="input-3",
            input_text="The research critique misses a scoring criterion.",
            candidate_absence="evaluation_criterion_missing",
        )

        verified = filter_verified_evidence(adapter.lookup(request))

        self.assertEqual([ref.id for ref in verified], ["evidence-evaluation-001"])
        self.assertTrue(verified[0].verified)

    def test_unverified_evidence_does_not_support_gate(self) -> None:
        adapter = load_fixture_adapter(CORPUS)
        request = CandidateEvidenceRequest(
            input_id="input-4",
            input_text="The policy note does not explain the exception field.",
            candidate_absence="policy_exception_missing",
        )

        raw = adapter.lookup(request)
        verified = filter_verified_evidence(raw)

        self.assertTrue(raw)
        self.assertEqual(verified, [])

    def test_adapter_does_not_assign_weight_or_promote(self) -> None:
        adapter = load_fixture_adapter(CORPUS)
        request = CandidateEvidenceRequest(
            input_id="input-5",
            input_text="The action point has no owner.",
            candidate_absence="owner_missing",
        )

        result = adapter.lookup(request)[0]

        self.assertFalse(hasattr(result, "weight"))
        self.assertFalse(hasattr(result, "status"))
        self.assertFalse(hasattr(result, "promoted"))

    def test_evidence_corpus_must_be_list(self) -> None:
        path = Path("/tmp/not_a_corpus.json")
        path.write_text("{}", encoding="utf-8")

        with self.assertRaises(ValueError):
            FixtureEvidenceAdapter.from_json_file(path)


if __name__ == "__main__":
    unittest.main()
