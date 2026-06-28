"""Audit replay helpers for agent-lab session decisions.

The lab keeps a detailed, lab-specific identity check (decision/seed/gate
matching) here, but the core "no weightless influence" invariant is enforced by
the upstream `shadowseed_agent` audit policy so the safety rule has a single
owner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from shadowseed_agent.audit_policy import (
    AgentInfluenceRecord,
    assert_no_weightless_influence,
)

from shadowseed_agent_lab.session_runner import SessionDecision, SessionResult


@dataclass(frozen=True)
class AuditFinding:
    decision_index: int
    seed_id: str
    action: str
    ok: bool
    reason: str


@dataclass(frozen=True)
class AuditReport:
    ok: bool
    findings: tuple[AuditFinding, ...]


def replay_session(result: SessionResult) -> AuditReport:
    findings = tuple(_check_decision(index, decision, result) for index, decision in enumerate(result.decisions))
    return AuditReport(ok=all(finding.ok for finding in findings), findings=findings)


def replay_sessions(results: Iterable[SessionResult]) -> AuditReport:
    findings: list[AuditFinding] = []
    for result in results:
        findings.extend(replay_session(result).findings)
    return AuditReport(ok=all(finding.ok for finding in findings), findings=tuple(findings))


def to_influence_records(result: SessionResult) -> list[AgentInfluenceRecord]:
    """Convert lab session decisions into upstream influence records."""

    seed = result.seed_after_gate
    return [
        AgentInfluenceRecord(
            seed_id=decision.seed_id,
            action=decision.action,
            seed_weight=seed.weight,
            seed_status=seed.status,
            allowed=decision.allowed,
            reason=decision.reason,
            gate_event_ref=decision.gate_event_ref,
        )
        for decision in result.decisions
    ]


def assert_no_weightless_influence_in_sessions(results: Iterable[SessionResult]) -> None:
    """Fail (via upstream policy) if any session allowed weightless influence.

    This delegates the hard safety invariant to the upstream
    `assert_no_weightless_influence`, raising `WeightlessInfluenceError` on a
    violation.
    """

    records: list[AgentInfluenceRecord] = []
    for result in results:
        records.extend(to_influence_records(result))
    assert_no_weightless_influence(records)


def _check_decision(index: int, decision: SessionDecision, result: SessionResult) -> AuditFinding:
    seed = result.seed_after_gate
    gate = result.gate_event
    decision_seed_id = decision.seed_id

    if decision.allowed and not decision_seed_id:
        return AuditFinding(index, decision_seed_id, decision.action, False, "missing_decision_seed_id")
    if decision.allowed and decision_seed_id != seed.id:
        return AuditFinding(index, decision_seed_id, decision.action, False, "decision_seed_mismatch")
    if decision.allowed and gate.seed_id != decision_seed_id:
        return AuditFinding(index, decision_seed_id, decision.action, False, "gate_seed_mismatch")
    if decision.allowed and decision.gate_event_ref != f"gate:{decision_seed_id}":
        return AuditFinding(index, decision_seed_id, decision.action, False, "missing_gate_ref")
    if decision.allowed and seed.weight <= 0.0:
        return AuditFinding(index, decision_seed_id, decision.action, False, "allowed_weightless_seed")
    if decision.allowed and seed.status != "PROMOTED":
        return AuditFinding(index, decision_seed_id, decision.action, False, "allowed_unpromoted_seed")
    if decision.allowed and not gate.promoted:
        return AuditFinding(index, decision_seed_id, decision.action, False, "gate_not_promoted")

    return AuditFinding(index, decision_seed_id, decision.action, True, "ok")
