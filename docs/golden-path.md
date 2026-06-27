# Golden Path

> Status: active lab path
> Scope: agent/RAG integration around upstream Shadow Seed Learning
> Upstream contract: `E-AI-MODEL/shadowseed`

## Purpose

This document defines the default path every demo, adapter, runner, and test in this lab should follow.

The lab does not redefine SSL. It uses the upstream `E-AI-MODEL/shadowseed` repository as the canonical source for SSL mechanics and evidence discipline.

The lab exists to answer one integration question:

```text
How can an agent or RAG layer use promoted SSL seeds without letting weightless seeds steer behavior?
```

## Canonical upstream responsibilities

The upstream `shadowseed` repository owns:

- seed lifecycle;
- trace and weight separation;
- Validation Gate behavior;
- contradiction handling;
- evidence discipline;
- core benchmark and regression evidence;
- the reusable `shadowseed_agent` safety contract.

This lab owns:

- fixture demos;
- RAG evidence adapters;
- session runners;
- audit replay around agent decisions;
- suggest-only agent boundaries.

## Non-negotiable invariant

```text
trace > 0 means the seed is present
weight = 0 means the seed does not steer
```

A seed with `weight <= 0` must not trigger retrieval, modify answer text, produce a warning, trigger a probe, or trigger an external action.

## Happy path

Evidence lookup is triggered by the input workflow, not by the weightless seed.

```text
input
  -> detect candidate absence
  -> create or observe seed
  -> seed starts weightless
  -> log seed presence
  -> input workflow requests candidate-evidence lookup
  -> verify evidence separately
  -> run Validation Gate with seed + verified evidence refs
  -> if blocked: no probe, no retrieval steering, no action
  -> if promoted: allow bounded probe suggestion
  -> log every decision
  -> audit replay must pass
```

The weightless seed may be passed to the gate as an object under evaluation. It may not itself cause retrieval, steer the query, or change the answer path.

## Gate path

A seed may influence an agent-side decision only when all conditions hold:

1. `seed.weight > 0.0`;
2. `seed.status == PROMOTED`;
3. a promotion exists in the gate log;
4. contradiction state does not block the seed;
5. evidence is verified and separate from generated model output.

If any condition fails, the adapter must return a blocked decision.

## RAG path

RAG is an evidence provider, not an influence authority.

Allowed:

```text
input/context -> candidate-evidence lookup -> evidence refs -> Validation Gate
seed candidate -> weightless seed -> Validation Gate
```

Not allowed:

```text
weightless seed -> retrieval steering -> answer change
```

RAG may supply candidate evidence from the input context. RAG may not assign weight, promote seeds, bypass the Validation Gate, or use a weightless seed as the retrieval driver.

## Probe path

A probe is allowed only after promotion.

Allowed:

```text
promoted seed + logged gate event -> bounded probe suggestion
```

Blocked:

```text
new/active/weightless seed -> probe suggestion
```

The first lab probes are suggestions only. They do not execute external actions.

## Audit path

Every seed-driven decision must be replayable.

Minimum audit failure:

```text
allowed=true and seed.weight <= 0
```

Minimum audit pass:

```text
blocked weightless seed
promoted gate-logged seed allowed for bounded probe
```

## Development order

1. deterministic multi-domain fixtures;
2. minimal evidence adapter;
3. session runner;
4. audit replay;
5. suggest-only external-action boundary.

Do not add live model behavior or external action execution before the deterministic path and audit replay are stable.

## Return-to-upstream rule

Move only generic improvements upstream:

- safety-contract fixes;
- audit helpers;
- reusable tests;
- claim-boundary documentation.

Keep lab-specific scenarios and demos in this repository.
