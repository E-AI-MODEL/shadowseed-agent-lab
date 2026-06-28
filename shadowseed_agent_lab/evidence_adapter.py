"""Input-driven evidence adapter for the Shadow Seed agent lab.

Upstream `E-AI-MODEL/shadowseed` owns the SSL core: seed lifecycle,
trace/weight separation, Validation Gate behavior, contradiction handling, and
promotion semantics.

This lab adapter does not fetch that logic dynamically and does not redefine it.
It sits before the upstream Validation Gate and prepares candidate evidence refs
from input/context.

The adapter deliberately does not accept a seed object as the lookup driver.
It accepts an input/candidate-evidence request and returns evidence references
that a later upstream-compatible Validation Gate step may evaluate.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from shadowseed_agent.agent_contract import (
    GENERATED_EVIDENCE_KINDS,
    evidence_can_support_gate,
)

# The set of generated (untrusted) evidence kinds is owned upstream. The lab
# does not maintain its own copy; it re-exports the upstream set so a change
# there cannot silently diverge here.
GENERATED_KINDS = GENERATED_EVIDENCE_KINDS


@dataclass(frozen=True)
class CandidateEvidenceRequest:
    """Input-driven lookup request.

    `candidate_absence` is a normalized absence label or phrase from the input
    workflow. It is not a seed id and carries no weight, status, or promotion.
    """

    input_id: str
    input_text: str
    candidate_absence: str


@dataclass(frozen=True)
class EvidenceRef:
    """Reference to candidate evidence returned by an adapter.

    `EvidenceRef` mirrors the evidence-discipline boundary used by upstream SSL:
    generated output is not verified evidence, and verification is separate from
    seed promotion.
    """

    id: str
    source: str
    kind: str
    text: str
    verified: bool
    supports_seed: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "EvidenceRef":
        return cls(
            id=str(data["id"]),
            source=str(data["source"]),
            kind=str(data["kind"]),
            text=str(data["text"]),
            verified=bool(data.get("verified", False)),
            supports_seed=(
                None if data.get("supports_seed") is None else str(data.get("supports_seed"))
            ),
        )

    def can_support_gate(self) -> bool:
        """Return whether this reference is eligible for gate support.

        The eligibility rule (verified, and not generated/model output) is owned
        by the upstream `shadowseed_agent` safety contract. The lab delegates to
        it instead of re-implementing the check.
        """

        return evidence_can_support_gate(self)


class FixtureEvidenceAdapter:
    """Deterministic fixture-backed adapter for lab demos and tests."""

    def __init__(self, evidence_refs: Iterable[EvidenceRef]):
        self._evidence_refs = tuple(evidence_refs)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "FixtureEvidenceAdapter":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("evidence corpus must be a JSON list")
        return cls(EvidenceRef.from_mapping(item) for item in raw)

    def lookup(self, request: CandidateEvidenceRequest) -> list[EvidenceRef]:
        """Return candidate evidence for an input-driven request.

        The request starts from input/context and candidate absence text. It does
        not accept a seed object and it never assigns seed weight or status.
        """

        if not isinstance(request, CandidateEvidenceRequest):
            raise TypeError("lookup requires CandidateEvidenceRequest, not a seed object")

        absence = _normalize(request.candidate_absence)
        input_text = _normalize(request.input_text)
        matches: list[EvidenceRef] = []

        for ref in self._evidence_refs:
            if _matches_request(ref, absence, input_text):
                matches.append(ref)

        return matches


def filter_verified_evidence(evidence_refs: Iterable[EvidenceRef]) -> list[EvidenceRef]:
    """Keep only evidence that may support the Validation Gate.

    Uses the upstream evidence-discipline check so generated/model output is
    never treated as verified support.
    """

    return [ref for ref in evidence_refs if evidence_can_support_gate(ref)]


def load_fixture_adapter(path: str | Path) -> FixtureEvidenceAdapter:
    """Load the fixture-backed adapter from a JSON corpus path."""

    return FixtureEvidenceAdapter.from_json_file(path)


def _matches_request(ref: EvidenceRef, absence: str, input_text: str) -> bool:
    supported = _normalize(ref.supports_seed or "")
    ref_text = _normalize(ref.text)

    if supported and (supported == absence or supported in input_text):
        return True
    return bool(absence and absence in ref_text)


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", "_").split())
