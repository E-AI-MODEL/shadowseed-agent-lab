"""Agent/RAG loop harness for the Shadow Seed agent lab.

This module turns the single-pass session runner into a bounded, multi-turn
loop with memory. It is the add-on surface another agent or RAG stack plugs
into:

- the **agent** seam is a `SeedProposer`: it reads input/context and proposes
  candidate absence labels. A real LLM can implement this. Its output is *not*
  evidence — proposed seeds start weightless and must still pass the gate.
- the **RAG** seam is an `EvidenceLookup` (the evidence adapter): it supplies
  candidate evidence for the gate. RAG never assigns weight or promotes a seed.

The loop:

1. asks the proposer for new candidate absences (excluding ones already seen);
2. runs each candidate through the gate-guarded session runner;
3. accumulates a gate log, so later turns see earlier logged promotions;
4. emits suggestion-only probes for promoted, gate-logged seeds;
5. stops at a fixpoint (no new seeds) or a hard iteration bound.

The hard "no weightless influence" invariant is enforced through the upstream
`shadowseed_agent` audit policy. The harness never re-implements SSL meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from shadowseed_agent.agent_contract import AgentSafetyContract
from shadowseed_agent.audit_policy import WeightlessInfluenceError

from shadowseed_agent_lab.audit_replay import (
    AuditReport,
    assert_no_weightless_influence_in_sessions,
    replay_sessions,
)
from shadowseed_agent_lab.session_runner import (
    AgentSessionRunner,
    GateEvent,
    GatePolicy,
    ProbeSuggestion,
    SessionRequest,
    SessionResult,
    normalize_seed_id,
)

DEFAULT_MAX_ITERATIONS = 32


@dataclass(frozen=True)
class Turn:
    """One unit of input/context handed to the loop."""

    input_id: str
    input_text: str


class SeedProposer(Protocol):
    """Agent seam: propose candidate absence labels from input/context.

    Output is a list of candidate absence labels. These are proposals only; they
    start weightless and carry no status, weight, or promotion. A label already
    present in ``known_seed_ids`` should not be proposed again.
    """

    def propose(self, input_text: str, known_seed_ids: frozenset[str]) -> list[str]:
        ...


class RetrieverProtocol(Protocol):
    """RAG seam: supply candidate evidence for the gate (never weight/promote).

    This mirrors the evidence adapter's ``lookup`` interface. RAG provides
    candidate evidence only; it never assigns weight, status, or promotion.
    """

    def lookup(self, request):  # noqa: ANN001 - mirrors EvidenceLookup
        ...


# Intent-revealing alias for add-on authors wiring a real retriever.
Retriever = RetrieverProtocol


@dataclass(frozen=True)
class MarkerSeedProposer:
    """Deterministic, rule-based proposer for demos and tests.

    Proposes a seed id when none of its markers appear in the input text. This
    stands in for an LLM-backed proposer without any live model call.
    """

    rules: tuple[tuple[str, tuple[str, ...]], ...]

    @classmethod
    def from_mapping(cls, mapping: dict[str, Iterable[str]]) -> "MarkerSeedProposer":
        return cls(tuple((seed_id, tuple(markers)) for seed_id, markers in mapping.items()))

    def propose(self, input_text: str, known_seed_ids: frozenset[str]) -> list[str]:
        lowered = input_text.lower()
        proposed: list[str] = []
        for seed_id, markers in self.rules:
            if normalize_seed_id(seed_id) in known_seed_ids:
                continue
            if not any(marker.lower() in lowered for marker in markers):
                proposed.append(seed_id)
        return proposed


@dataclass(frozen=True)
class LoopResult:
    """Outcome of a bounded loop run."""

    turns_run: int
    iterations: int
    sessions: tuple[SessionResult, ...]
    probe_suggestions: tuple[ProbeSuggestion, ...]
    gate_log: tuple[GateEvent, ...]
    audit: AuditReport
    safe: bool
    safety_error: str | None = None

    @property
    def known_seed_ids(self) -> frozenset[str]:
        return frozenset(result.seed_after_gate.id for result in self.sessions)

    @property
    def promoted_seed_ids(self) -> frozenset[str]:
        return frozenset(
            result.seed_after_gate.id
            for result in self.sessions
            if result.gate_event.promoted
        )


class AgentLabHarness:
    """Bounded agent/RAG loop around the gate-guarded session runner."""

    def __init__(
        self,
        proposer: SeedProposer,
        evidence_lookup: "RetrieverProtocol",
        gate_policy: GatePolicy | None = None,
        contract: AgentSafetyContract | None = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ):
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        self._proposer = proposer
        self._runner = AgentSessionRunner(
            evidence_lookup,
            gate_policy=gate_policy,
            contract=contract,
        )
        self._max_iterations = max_iterations

    def run_loop(self, turns: Iterable[Turn]) -> LoopResult:
        known: set[str] = set()
        gate_log: list[GateEvent] = []
        sessions: list[SessionResult] = []
        probes: list[ProbeSuggestion] = []
        iterations = 0
        turns_run = 0

        for turn in turns:
            turns_run += 1
            # Per-turn convergence loop: keep proposing until the proposer adds
            # nothing new (fixpoint) or the iteration bound is hit.
            while iterations < self._max_iterations:
                candidates = self._proposer.propose(turn.input_text, frozenset(known))
                new = [c for c in candidates if normalize_seed_id(c) not in known]
                if not new:
                    break
                for candidate in new:
                    if iterations >= self._max_iterations:
                        break
                    # Skip within-batch duplicates and aliases (e.g. "owner_missing"
                    # and "owner-missing") that normalize to a seed already handled
                    # this pass, so memory/dedup holds and the iteration budget is
                    # not spent on repeated work.
                    if normalize_seed_id(candidate) in known:
                        continue
                    iterations += 1
                    result = self._runner.run(
                        SessionRequest(turn.input_id, turn.input_text, candidate)
                    )
                    known.add(result.seed_after_gate.id)
                    gate_log.append(result.gate_event)
                    sessions.append(result)
                    if result.probe_suggestion is not None:
                        probes.append(result.probe_suggestion)

        audit = replay_sessions(sessions)
        safe = True
        safety_error: str | None = None
        try:
            assert_no_weightless_influence_in_sessions(sessions)
        except WeightlessInfluenceError as exc:  # pragma: no cover - safety net
            safe = False
            safety_error = str(exc)

        return LoopResult(
            turns_run=turns_run,
            iterations=iterations,
            sessions=tuple(sessions),
            probe_suggestions=tuple(probes),
            gate_log=tuple(gate_log),
            audit=audit,
            safe=safe and audit.ok,
            safety_error=safety_error,
        )
