# Upstream Contract

`E-AI-MODEL/shadowseed` is the source of truth for Shadow Seed Learning semantics.

## Lab relation

`E-AI-MODEL/shadowseed-agent-lab` is a sister repo for agent/RAG integration experiments. It should integrate around upstream SSL, not replace or reinterpret it.

## How the lab consumes upstream

The lab declares `shadowseed` as a package dependency and **imports** the
upstream safety helpers rather than copying them:

- `shadowseed_agent.agent_contract.AgentSafetyContract` / `InfluenceAction`;
- `shadowseed_agent.agent_contract.evidence_can_support_gate` /
  `GENERATED_EVIDENCE_KINDS`;
- `shadowseed_agent.audit_policy.assert_no_weightless_influence`.

`tests/test_upstream_integration.py` fails if the lab stops delegating these or
diverges from the upstream generated-evidence set.

## Upstream-owned semantics

Do not redefine these in the lab repo:

- seed lifecycle;
- trace and weight meaning;
- Validation Gate behavior;
- contradiction handling;
- promotion semantics;
- evidence discipline;
- benchmark interpretation;
- production-readiness claims.

## Lab-owned behavior

The lab may define:

- fixture corpora;
- input-driven evidence adapters;
- fixture-only gate policies for deterministic tests;
- policy seams for future upstream-compatible gate adapters;
- suggestion-only probe boundaries;
- audit replay over lab session decisions;
- reviewer/agent workflow packaging.

## Decision rule

If a change decides what SSL means, it belongs upstream.

If a change decides how an agent integration safely calls, wraps, reviews, or audits SSL boundaries, it may belong in the lab.

## Claim rule

Use research/prototype language unless the upstream repo has tests, benchmarks, and documented evidence for a stronger claim.
