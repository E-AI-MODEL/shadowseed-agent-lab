"""Bounded session runner for the Shadow Seed agent lab.

This module wires input/context to a weightless seed record, input-driven
evidence lookup, a gate-policy seam, a promoted-only probe suggestion, and a
decision log.

The default gate policy is fixture-only. The source repo `shadowseed` remains the
owner of SSL meanings such as lifecycle, promotion, and trace/weight behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from shadowseed_agent_lab.evidence_adapter import (
    CandidateEvidenceRequest,
    EvidenceRef,
    filter_verified_evidence,
)

NEW_STATUS = "NEW"
PROMOTED_STATUS = "PROMOTED"
BLOCKED_STATUS = "BLOCKED"
PROMOTED_WEIGHT = 0.6
FIXTURE_GATE_POLICY = "fixture_gate_policy"


class EvidenceLookup(Protocol):
    """Input-driven evidence lookup interface."""

    def lookup(self, request: CandidateEvidenceRequest) -> list[EvidenceRef]:
        """Return candidate evidence for an input-driven request."""


class GatePolicy(Protocol):
    """Policy seam for gate decisions in lab sessions."""

    def decide(self, seed: "SessionSeed", verified_refs: tuple[EvidenceRef, ...]) -> "GateEvent":
        """Return a gate event for one seed under evaluation."""


@dataclass(frozen=True)
class SessionRequest:
    input_id: str
    input_text: str
    candidate_absence: str


@dataclass(frozen=True)
class SessionSeed:
    id: str
    trace: float
    weight: float
    status: str


@dataclass(frozen=True)
class GateEvent:
    seed_id: str
    promoted: bool
    status_after: str
    weight_after: float
    evidence_ids: tuple[str, ...]
    reason: str
    policy: str


@dataclass(frozen=True)
class ProbeSuggestion:
    seed_id: str
    probe: str
    gate_event_ref: str
    suggestion_only: bool = True


@dataclass(frozen=True)
class SessionDecision:
    seed_id: str
    action: str
    allowed: bool
    reason: str
    gate_event_ref: str | None = None


@dataclass(frozen=True)
class SessionResult:
    input_id: str
    seed_before_gate: SessionSeed
    seed_after_gate: SessionSeed
    evidence_refs: tuple[EvidenceRef, ...]
    verified_evidence_refs: tuple[EvidenceRef, ...]
    gate_event: GateEvent
    probe_suggestion: ProbeSuggestion | None
    decisions: tuple[SessionDecision, ...]


class FixtureGatePolicy:
    """Deterministic fixture-only policy for lab tests."""

    name = FIXTURE_GATE_POLICY

    def decide(self, seed: SessionSeed, verified_refs: tuple[EvidenceRef, ...]) -> GateEvent:
        supporting_refs = tuple(
            ref for ref in verified_refs if _evidence_supports_seed(ref, seed.id)
        )
        if not supporting_refs:
            return GateEvent(
                seed_id=seed.id,
                promoted=False,
                status_after=BLOCKED_STATUS,
                weight_after=0.0,
                evidence_ids=(),
                reason="missing_verified_support",
                policy=self.name,
            )

        return GateEvent(
            seed_id=seed.id,
            promoted=True,
            status_after=PROMOTED_STATUS,
            weight_after=PROMOTED_WEIGHT,
            evidence_ids=tuple(ref.id for ref in supporting_refs),
            reason="fixture_verified_support",
            policy=self.name,
        )


class AgentSessionRunner:
    """Small deterministic observe-to-probe runner."""

    def __init__(self, evidence_lookup: EvidenceLookup, gate_policy: GatePolicy | None = None):
        self._evidence_lookup = evidence_lookup
        self._gate_policy = gate_policy or FixtureGatePolicy()

    def run(self, request: SessionRequest) -> SessionResult:
        seed_id = _normalize(request.candidate_absence)
        if not seed_id:
            raise ValueError("candidate_absence must not be empty")

        seed = SessionSeed(
            id=seed_id,
            trace=1.0,
            weight=0.0,
            status=NEW_STATUS,
        )

        evidence_request = CandidateEvidenceRequest(
            input_id=request.input_id,
            input_text=request.input_text,
            candidate_absence=request.candidate_absence,
        )
        evidence_refs = tuple(self._evidence_lookup.lookup(evidence_request))
        verified_refs = tuple(filter_verified_evidence(evidence_refs))

        gate_event = self._gate_policy.decide(seed, verified_refs)
        seed_after_gate = SessionSeed(
            id=seed.id,
            trace=seed.trace,
            weight=gate_event.weight_after,
            status=gate_event.status_after,
        )

        probe_decision = _decide_probe(seed_after_gate, gate_event)
        probe = None
        if probe_decision.allowed and probe_decision.gate_event_ref is not None:
            probe = ProbeSuggestion(
                seed_id=seed_after_gate.id,
                probe=f"ask_for_{seed_after_gate.id}",
                gate_event_ref=probe_decision.gate_event_ref,
            )

        return SessionResult(
            input_id=request.input_id,
            seed_before_gate=seed,
            seed_after_gate=seed_after_gate,
            evidence_refs=evidence_refs,
            verified_evidence_refs=verified_refs,
            gate_event=gate_event,
            probe_suggestion=probe,
            decisions=(probe_decision,),
        )


def _decide_probe(seed: SessionSeed, gate_event: GateEvent) -> SessionDecision:
    if seed.weight <= 0.0:
        return SessionDecision(seed.id, "probe", False, "weightless_seed")
    if seed.status != PROMOTED_STATUS:
        return SessionDecision(seed.id, "probe", False, "seed_not_promoted")
    if not gate_event.promoted or gate_event.seed_id != seed.id:
        return SessionDecision(seed.id, "probe", False, "missing_logged_promotion")
    return SessionDecision(
        seed.id,
        "probe",
        True,
        "allowed_promoted_gate_logged",
        gate_event_ref=f"gate:{gate_event.seed_id}",
    )


def _evidence_supports_seed(ref: EvidenceRef, seed_id: str) -> bool:
    if not seed_id:
        return False
    supported = _normalize(ref.supports_seed or "")
    ref_text = _normalize(ref.text)
    return bool((supported and supported == seed_id) or seed_id in ref_text)


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", "_").split())
