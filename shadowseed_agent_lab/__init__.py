"""Installable agent/RAG add-on and loop harness for Shadow Seed Learning.

The lab consumes the upstream `shadowseed_agent` safety contract directly; it
does not redefine SSL semantics. Public surface:

- evidence adapter (RAG seam) and the gate-guarded single-pass session runner;
- the bounded multi-turn loop harness (`AgentLabHarness`) and its agent seam
  (`SeedProposer` / `MarkerSeedProposer`);
- audit replay helpers, including the upstream-backed weightless-influence check.
"""

from shadowseed_agent_lab.evidence_adapter import (
    CandidateEvidenceRequest,
    EvidenceRef,
    FixtureEvidenceAdapter,
    filter_verified_evidence,
    load_fixture_adapter,
)
from shadowseed_agent_lab.session_runner import (
    AgentSessionRunner,
    FixtureGatePolicy,
    GateEvent,
    ProbeSuggestion,
    SessionDecision,
    SessionRequest,
    SessionResult,
    SessionSeed,
    normalize_seed_id,
)
from shadowseed_agent_lab.audit_replay import (
    AuditFinding,
    AuditReport,
    assert_no_weightless_influence_in_sessions,
    replay_session,
    replay_sessions,
    to_influence_records,
)
from shadowseed_agent_lab.harness import (
    AgentLabHarness,
    LoopResult,
    MarkerSeedProposer,
    Retriever,
    SeedProposer,
    Turn,
)

__all__ = [
    "AgentLabHarness",
    "AgentSessionRunner",
    "AuditFinding",
    "AuditReport",
    "CandidateEvidenceRequest",
    "EvidenceRef",
    "FixtureEvidenceAdapter",
    "FixtureGatePolicy",
    "GateEvent",
    "LoopResult",
    "MarkerSeedProposer",
    "ProbeSuggestion",
    "Retriever",
    "SeedProposer",
    "SessionDecision",
    "SessionRequest",
    "SessionResult",
    "SessionSeed",
    "Turn",
    "assert_no_weightless_influence_in_sessions",
    "filter_verified_evidence",
    "load_fixture_adapter",
    "normalize_seed_id",
    "replay_session",
    "replay_sessions",
    "to_influence_records",
]
