"""Input-driven evidence adapter for the Shadow Seed agent lab.

The adapter deliberately does not accept a seed object as the lookup driver.
It accepts an input/candidate-evidence request and returns evidence references
that a later Validation Gate step may evaluate.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

GENERATED_KINDS = {
    "completion",
    "generated_completion",
    "llm_output",
    "model_output",
}


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
    """Reference to candidate evidence returned by an adapter."""

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
        """Return whether this reference is eligible for gate support."""

        return self.verified and self.kind.strip().lower() not in GENERATED_KINDS


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

        absence = _normalize(request.candidate_absence)
        input_text = _normalize(request.input_text)
        matches: list[EvidenceRef] = []

        for ref in self._evidence_refs:
            supported = _normalize(ref.supports_seed or "")
            ref_text = _normalize(ref.text)
            if supported == absence or absence in ref_text or supported in input_text:
                matches.append(ref)

        return matches


def filter_verified_evidence(evidence_refs: Iterable[EvidenceRef]) -> list[EvidenceRef]:
    """Keep only evidence that may support the Validation Gate."""

    return [ref for ref in evidence_refs if ref.can_support_gate()]


def load_fixture_adapter(path: str | Path) -> FixtureEvidenceAdapter:
    """Load the fixture-backed adapter from a JSON corpus path."""

    return FixtureEvidenceAdapter.from_json_file(path)


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace("-", "_").split())
