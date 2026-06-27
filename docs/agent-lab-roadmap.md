# Agent Lab Roadmap

> Status: initial lab plan
> Date: 2026-06-27
> Scope: experimental agent/RAG integration boundary
> Claim boundary: not production-ready

## Goal

Build a safe, auditable agent/RAG lab around Shadow Seed Learning without changing the upstream SSL core claim boundary.

The lab should answer one practical question:

```text
Can promoted, gate-logged SSL seeds safely guide retrieval, probes, warnings, or suggestions without allowing weightless seeds to steer behavior?
```

## Phase 0: Scope And Claim Boundary

Purpose: make the lab boundary explicit before building behavior.

Done when:

- README explains this is experimental;
- non-goals are explicit;
- upstream relationship is documented;
- safety rules are visible.

## Phase 1: Fixture-Driven School Notes Demo

Purpose: create a deterministic demo before introducing live models or live tools.

Input examples:

- meeting notes;
- policy action points;
- incomplete task lists;
- school-process notes.

Expected output:

- seed candidates;
- gate blocked or promoted state;
- suggested follow-up probe;
- audit log result.

## Phase 2: Minimal RAG Evidence Adapter

Purpose: let retrieval provide evidence to the Validation Gate without letting retrieval itself be driven by weightless seeds.

Rules:

- RAG may provide candidate evidence;
- RAG may not promote seeds directly;
- generated text is not verified evidence;
- only verified evidence may support a gate decision.

## Phase 3: Agent Session Runner

Purpose: implement a small observe-to-probe loop.

Flow:

```text
user input
  -> candidate seed detection
  -> weightless storage
  -> evidence lookup
  -> Validation Gate
  -> promoted-only probe suggestion
  -> decision log
```

## Phase 4: Audit Replay

Purpose: replay all seed-driven decisions and fail if weightless influence occurred.

Minimum invariant:

```text
No decision with allowed=true may reference a seed with weight <= 0.
```

## Phase 5: Suggest-Only External Action Boundary

Purpose: explore how an agent may suggest actions without executing them.

Rules:

- suggestions only;
- no external execution;
- every suggestion must cite promoted seed and gate event;
- human approval remains outside this lab until later hardening.

## Return-To-Upstream Policy

Send upstream only generic improvements:

- safety-contract fixes;
- tests;
- audit helpers;
- claim-boundary docs.

Keep lab-specific demos and scenarios here.
