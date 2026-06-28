from __future__ import annotations

from dataclasses import dataclass
import unittest

from shadowseed_agent_lab import (
    AgentLabHarness,
    EvidenceRef,
    FixtureEvidenceAdapter,
    MarkerSeedProposer,
    Turn,
)


def _verified(seed_id: str) -> EvidenceRef:
    return EvidenceRef(
        id=f"ev-{seed_id}",
        source="fixture#notes",
        kind="fixture_note",
        text=f"{seed_id} is required.",
        verified=True,
        supports_seed=seed_id,
    )


@dataclass
class ScriptedProposer:
    """Proposer that emits scripted candidates, honoring known_seed_ids."""

    candidates: list[str]

    def propose(self, input_text: str, known_seed_ids: frozenset[str]) -> list[str]:
        return [c for c in self.candidates if c not in known_seed_ids]


class HarnessLoopTests(unittest.TestCase):
    def test_loop_promotes_supported_seed_and_blocks_unsupported(self) -> None:
        adapter = FixtureEvidenceAdapter([_verified("owner_missing")])
        harness = AgentLabHarness(
            ScriptedProposer(["owner_missing", "deadline_missing"]),
            adapter,
        )

        result = harness.run_loop([Turn("doc-1", "an item without an owner or deadline")])

        self.assertEqual(len(result.sessions), 2)
        self.assertEqual(result.promoted_seed_ids, frozenset({"owner_missing"}))
        self.assertEqual(
            {p.probe for p in result.probe_suggestions}, {"ask_for_owner_missing"}
        )
        self.assertTrue(result.audit.ok)
        self.assertTrue(result.safe)

    def test_weightless_seeds_never_get_a_probe(self) -> None:
        harness = AgentLabHarness(
            ScriptedProposer(["owner_missing", "deadline_missing"]),
            FixtureEvidenceAdapter([]),
        )

        result = harness.run_loop([Turn("doc", "text")])

        self.assertEqual(result.probe_suggestions, ())
        self.assertTrue(result.safe)
        for session in result.sessions:
            self.assertEqual(session.seed_after_gate.weight, 0.0)
            self.assertIsNone(session.probe_suggestion)

    def test_loop_has_memory_and_dedupes_across_turns(self) -> None:
        adapter = FixtureEvidenceAdapter([_verified("owner_missing")])
        harness = AgentLabHarness(ScriptedProposer(["owner_missing"]), adapter)

        result = harness.run_loop(
            [Turn("doc-1", "no owner"), Turn("doc-2", "still no owner")]
        )

        self.assertEqual(result.turns_run, 2)
        # owner_missing is proposed once; the second turn sees it as known.
        self.assertEqual(len(result.sessions), 1)
        self.assertEqual(result.sessions[0].input_id, "doc-1")

    def test_loop_converges_to_fixpoint(self) -> None:
        adapter = FixtureEvidenceAdapter([_verified("owner_missing")])
        harness = AgentLabHarness(
            ScriptedProposer(["owner_missing", "deadline_missing"]),
            adapter,
            max_iterations=100,
        )

        result = harness.run_loop([Turn("doc", "text")])

        # Two distinct candidates -> two iterations, then the proposer returns
        # nothing new and the loop stops well under the iteration bound.
        self.assertEqual(result.iterations, 2)

    def test_iteration_bound_is_respected(self) -> None:
        class EndlessProposer:
            def __init__(self) -> None:
                self._n = 0

            def propose(self, input_text: str, known_seed_ids: frozenset[str]) -> list[str]:
                self._n += 1
                return [f"seed_{self._n}"]

        harness = AgentLabHarness(EndlessProposer(), FixtureEvidenceAdapter([]), max_iterations=5)

        result = harness.run_loop([Turn("doc", "text")])

        self.assertEqual(result.iterations, 5)
        self.assertTrue(result.safe)

    def test_marker_proposer_only_proposes_absent_markers(self) -> None:
        proposer = MarkerSeedProposer.from_mapping(
            {"owner_missing": ["owner:"], "deadline_missing": ["deadline:"]}
        )

        proposed = proposer.propose("owner: alice, but nothing else", frozenset())

        self.assertEqual(proposed, ["deadline_missing"])

    def test_zero_max_iterations_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AgentLabHarness(ScriptedProposer([]), FixtureEvidenceAdapter([]), max_iterations=0)


if __name__ == "__main__":
    unittest.main()
