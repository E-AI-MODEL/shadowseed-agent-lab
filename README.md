# shadowseed-agent-lab

Experimental agent/RAG integration lab for Shadow Seed Learning.

This repository explores how SSL seeds can safely interact with retrieval,
probes, warnings, and agent suggestions.

It is not a production agent.

## Safety boundary

- A seed with `weight <= 0` must not trigger retrieval.
- A seed with `weight <= 0` must not change answer text.
- A seed with `weight <= 0` must not trigger external actions.
- LLM output is not verified evidence.
- Only `PROMOTED` seeds with a logged Validation Gate event may trigger probes.
- External action execution is out of scope until suggest-only mode is audited.

## Relationship to upstream

Upstream `E-AI-MODEL/shadowseed` contains the SSL core, benchmarks, and evidence discipline.

This lab contains experimental agent/RAG integration work.

## Initial lab path

The first goal is not an autonomous agent. The first goal is a safe sandbox that can prove this invariant:

```text
trace > 0 means the seed is present
weight = 0 means the seed does not steer
```

Planned first layers:

1. fixture-driven school-notes demo;
2. minimal RAG evidence adapter;
3. agent session runner;
4. audit replay for seed-driven decisions;
5. suggest-only external-action boundary.

## Non-goals

This repository does not yet:

- execute external actions;
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
