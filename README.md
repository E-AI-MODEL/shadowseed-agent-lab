# shadowseed-agent-lab

Experimental agent/RAG integration lab for Shadow Seed Learning.

This repository explores how SSL seeds can safely interact with retrieval,
probes, warnings, and agent suggestions across multiple domains.

It is not a production agent.

## Foundation status

The first agent-lab foundation is complete as a research/prototype harness.

Implemented layers:

1. fixture-driven multi-domain absence demo;
2. minimal input-driven evidence adapter;
3. bounded session runner;
4. fixture-only gate-policy seam;
5. PR safety checklist and local test gate;
6. audit replay for seed-driven decisions;
7. reviewer profile and Skill foundation.

Candidate release tag for the foundation snapshot:

```text
v0.1.0-ssl-agent-lab-foundation
```

No release tag is created by this README update.

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
- [`docs/pr-safety-checklist.md`](docs/pr-safety-checklist.md)

## Agent and Skill layer

Reusable lab review workflow files:

- [`agents/shadowseed-agent-lab-reviewer.md`](agents/shadowseed-agent-lab-reviewer.md)
- [`skills/shadowseed-agent-lab/SKILL.md`](skills/shadowseed-agent-lab/SKILL.md)
- [`skills/shadowseed-agent-lab/references/upstream-contract.md`](skills/shadowseed-agent-lab/references/upstream-contract.md)
- [`skills/shadowseed-agent-lab/references/review-checklist.md`](skills/shadowseed-agent-lab/references/review-checklist.md)

`skills/shadowseed-agent-lab/agents/openai.yaml` is OpenAI UI metadata only. The lab workflow and Skill instructions are not OpenAI-only.

## Test gate

Before merging lab behavior changes, run:

```bash
python -m unittest discover -s tests
```

Record the result in the PR body or review comment.

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
