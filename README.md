# shadowseed-agent-lab

Experimental agent/RAG integration lab for Shadow Seed Learning.

This repository explores how SSL seeds can safely interact with retrieval,
probes, warnings, and agent suggestions across multiple domains.

It is not a production agent.

## Safety boundary

- A seed with `weight <= 0` must not trigger retrieval.
- A seed with `weight <= 0` must not change answer text.
- A seed with `weight <= 0` must not trigger downstream behavior.
- LLM output is not verified evidence.
- Only `PROMOTED` seeds with a logged Validation Gate event may trigger probes.
- Downstream execution is out of scope until suggest-only mode is audited.

## Upstream contract

Upstream `E-AI-MODEL/shadowseed` contains the SSL core, benchmarks, evidence discipline, and reusable `shadowseed_agent` safety helpers.

This lab does not redefine SSL. It builds agent/RAG experiments around the upstream contract:

```text
trace > 0 means the seed is present
weight = 0 means the seed does not steer
```

## Golden path and architecture decisions

Start here before adding new behavior:

- [`docs/golden-path.md`](docs/golden-path.md)
- [`docs/architecture-decisions/README.md`](docs/architecture-decisions/README.md)
- [`docs/architecture-decisions/0001-agent-lab-boundary.md`](docs/architecture-decisions/0001-agent-lab-boundary.md)
- [`docs/architecture-decisions/0002-rag-as-evidence-not-influence.md`](docs/architecture-decisions/0002-rag-as-evidence-not-influence.md)

## Initial lab path

The first goal is not an autonomous agent. The first goal is a safe sandbox that can prove the upstream invariant across agent/RAG boundaries.

Planned first layers:

1. fixture-driven multi-domain absence demo;
2. minimal RAG evidence adapter;
3. agent session runner;
4. audit replay for seed-driven decisions;
5. suggest-only downstream boundary.

## Fixture domains

The first fixture set should include several domains so SSL is not framed as school-specific:

- project planning;
- policy or compliance notes;
- incident review;
- product requirements;
- research critique;
- optional education/school notes as one example, not the core scope.

## Non-goals

This repository does not yet:

- execute downstream behavior;
- update external systems;
- run autonomous workflows;
- claim production readiness.

## Upstream sync

This repository is a sister repo, not a GitHub fork. Keep upstream explicit:

```bash
git remote add upstream https://github.com/E-AI-MODEL/shadowseed.git
git fetch upstream
```

Merge upstream deliberately only when the lab needs a newer SSL core.
