# 0001: Agent Lab Boundary Around Upstream SSL

## Status

Accepted.

## Context

`shadowseed-agent-lab` is a sister repository for agent and RAG integration experiments around Shadow Seed Learning.

The upstream `E-AI-MODEL/shadowseed` repository defines the SSL core. This lab should not re-open those core mechanics each time it adds an agent-side experiment.

The upstream contract this lab depends on is:

```text
trace > 0 means the seed is present
weight = 0 means the seed does not steer
```

## Decision

`shadowseed-agent-lab` treats `E-AI-MODEL/shadowseed` as the canonical source for SSL mechanics.

Upstream owns:

- seed lifecycle;
- trace and weight separation;
- Validation Gate behavior;
- contradiction handling;
- evidence discipline;
- core tests and benchmark evidence;
- reusable `shadowseed_agent` safety helpers.

This lab owns:

- deterministic fixture demos;
- agent and RAG integration experiments;
- evidence adapter prototypes;
- session runners;
- audit replay around agent decisions;
- suggest-only downstream boundaries.

## Consequences

The lab can move faster because it does not need to re-prove upstream SSL mechanics in every PR.

The lab must preserve the upstream invariant at every agent boundary.

A seed may influence an agent-side decision only when it has positive weight, `PROMOTED` status, and a matching logged gate event.

Weightless seeds may be observed, stored, logged, displayed, and tested. They may not steer retrieval, probes, warnings, answer changes, or downstream behavior.

## Boundary

This decision makes the lab `harness-oriented` for integration experiments. It does not turn the lab into a production runtime.
