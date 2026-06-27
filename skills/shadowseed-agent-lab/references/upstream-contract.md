# Upstream Contract

`E-AI-MODEL/shadowseed` is the source of truth for Shadow Seed Learning semantics.

## Lab relation

`E-AI-MODEL/shadowseed-agent-lab` is a sister repo for agent/RAG integration experiments. It should integrate around upstream SSL, not replace or reinterpret it.

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
