"""Deterministic multi-domain absence demo for the agent lab.

This demo intentionally avoids live models. It uses small fixtures and simple
string checks to prove the first lab invariant: detected seeds start weightless,
and only promoted, gate-logged seeds may suggest a probe.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@dataclass(frozen=True)
class Rule:
    seed_id: str
    required_markers: tuple[str, ...]
    probe: str


@dataclass(frozen=True)
class DemoSeed:
    seed_id: str
    fixture: str
    weight: float
    status: str
    gate: str
    probe: str | None
    evidence_ref: str | None


@dataclass(frozen=True)
class AuditRecord:
    seed_id: str
    fixture: str
    allowed: bool
    seed_weight: float
    action: str
    reason: str


DOMAIN_RULES: dict[str, tuple[Rule, ...]] = {
    "project_plan.md": (
        Rule("owner_missing", ("owner:",), "ask_for_owner"),
        Rule("deadline_missing", ("deadline:",), "ask_for_deadline"),
        Rule("decision_status_missing", ("status:",), "ask_for_decision_status"),
    ),
    "compliance_note.md": (
        Rule("policy_exception_missing", ("exception:",), "ask_for_policy_exception"),
        Rule("evidence_reference_missing", ("evidence:",), "ask_for_evidence_reference"),
    ),
    "incident_review.md": (
        Rule("mitigation_owner_missing", ("mitigation owner:",), "ask_for_mitigation_owner"),
        Rule("deadline_missing", ("deadline:",), "ask_for_deadline"),
    ),
    "product_requirements.md": (
        Rule("acceptance_criterion_missing", ("acceptance criterion:",), "ask_for_acceptance_criterion"),
        Rule("evidence_reference_missing", ("evidence:",), "ask_for_evidence_reference"),
    ),
    "research_critique.md": (
        Rule("evaluation_criterion_missing", ("evaluation criterion:",), "ask_for_evaluation_criterion"),
        Rule("evidence_reference_missing", ("evidence:",), "ask_for_evidence_reference"),
    ),
    "education_note.md": (
        Rule("owner_missing", ("owner:",), "ask_for_owner"),
        Rule("deadline_missing", ("deadline:",), "ask_for_deadline"),
    ),
}


PROMOTION_MARKERS: dict[str, str] = {
    "deadline_missing": "verified evidence: deadline required",
    "mitigation_owner_missing": "verified evidence: mitigation owner required",
    "evaluation_criterion_missing": "verified evidence: evaluation criterion required",
}


def _read_fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _missing_rule(text: str, rule: Rule) -> bool:
    lowered = text.lower()
    return not any(marker in lowered for marker in rule.required_markers)


def _has_verified_evidence(text: str, seed_id: str) -> bool:
    marker = PROMOTION_MARKERS.get(seed_id)
    if marker is None:
        return False
    return marker in text.lower()


def evaluate_fixture(path: Path) -> list[DemoSeed]:
    text = _read_fixture(path)
    rules = DOMAIN_RULES.get(path.name, ())
    seeds: list[DemoSeed] = []

    for rule in rules:
        if not _missing_rule(text, rule):
            continue

        verified = _has_verified_evidence(text, rule.seed_id)
        if verified:
            seeds.append(
                DemoSeed(
                    seed_id=rule.seed_id,
                    fixture=path.name,
                    weight=0.6,
                    status="PROMOTED",
                    gate="promoted",
                    probe=rule.probe,
                    evidence_ref=f"{path.name}#verified-evidence",
                )
            )
        else:
            seeds.append(
                DemoSeed(
                    seed_id=rule.seed_id,
                    fixture=path.name,
                    weight=0.0,
                    status="NEW",
                    gate="blocked",
                    probe=None,
                    evidence_ref=None,
                )
            )

    return seeds


def audit_seed(seed: DemoSeed) -> AuditRecord:
    allowed = seed.probe is not None
    if allowed and seed.weight <= 0.0:
        reason = "violation_weightless_influence"
    elif allowed:
        reason = "allowed_promoted_gate_logged"
    else:
        reason = "blocked_weightless_seed"

    return AuditRecord(
        seed_id=seed.seed_id,
        fixture=seed.fixture,
        allowed=allowed,
        seed_weight=seed.weight,
        action="probe",
        reason=reason,
    )


def run_demo(fixture_dir: Path = FIXTURE_DIR) -> list[DemoSeed]:
    results: list[DemoSeed] = []
    for fixture_name in sorted(DOMAIN_RULES):
        results.extend(evaluate_fixture(fixture_dir / fixture_name))
    return results


def format_seed(seed: DemoSeed) -> str:
    probe = seed.probe or "none"
    evidence = seed.evidence_ref or "none"
    return "\n".join(
        [
            f"fixture: {seed.fixture}",
            f"seed_detected: {seed.seed_id}",
            f"seed_weight: {seed.weight}",
            f"status: {seed.status}",
            f"gate: {seed.gate}",
            f"probe: {probe}",
            f"evidence: {evidence}",
            f"audit: {audit_seed(seed).reason}",
        ]
    )


def main() -> None:
    for seed in run_demo():
        print(format_seed(seed))
        print()


if __name__ == "__main__":
    main()
