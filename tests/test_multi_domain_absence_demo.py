from __future__ import annotations

import unittest

from examples.agent_lab.multi_domain_absence_demo import audit_seed, format_seed, run_demo


class MultiDomainAbsenceDemoTests(unittest.TestCase):
    def test_demo_covers_multiple_domains(self) -> None:
        results = run_demo()
        fixtures = {seed.fixture for seed in results}

        self.assertGreaterEqual(len(fixtures), 3)
        self.assertIn("project_plan.md", fixtures)
        self.assertIn("incident_review.md", fixtures)
        self.assertIn("research_critique.md", fixtures)

    def test_detected_seeds_include_blocked_and_promoted_states(self) -> None:
        results = run_demo()
        gates = {seed.gate for seed in results}

        self.assertIn("blocked", gates)
        self.assertIn("promoted", gates)

    def test_weightless_seeds_do_not_get_probe(self) -> None:
        for seed in run_demo():
            if seed.weight <= 0.0:
                self.assertIsNone(seed.probe)
                self.assertEqual(seed.status, "NEW")
                self.assertEqual(seed.gate, "blocked")

    def test_promoted_seeds_get_probe_and_evidence_ref(self) -> None:
        promoted = [seed for seed in run_demo() if seed.status == "PROMOTED"]

        self.assertTrue(promoted)
        for seed in promoted:
            self.assertGreater(seed.weight, 0.0)
            self.assertEqual(seed.gate, "promoted")
            self.assertIsNotNone(seed.probe)
            self.assertIsNotNone(seed.evidence_ref)

    def test_audit_replay_flags_no_weightless_allowed_influence(self) -> None:
        for seed in run_demo():
            record = audit_seed(seed)
            self.assertFalse(record.allowed and record.seed_weight <= 0.0)

    def test_format_seed_contains_decision_log_fields(self) -> None:
        rendered = format_seed(run_demo()[0])

        self.assertIn("fixture:", rendered)
        self.assertIn("seed_detected:", rendered)
        self.assertIn("seed_weight:", rendered)
        self.assertIn("gate:", rendered)
        self.assertIn("audit:", rendered)


if __name__ == "__main__":
    unittest.main()
