# shadowseed-agent-lab

Installable agent/RAG add-on and loop harness for Shadow Seed Learning.

This package wraps SSL seeds in a safe, auditable agent loop: it detects
candidate absences, runs them through the upstream Validation Gate contract,
and emits suggestion-only probes for promoted, gate-logged seeds across
multiple domains.

The safety boundary below is a hard design contract, not a maturity caveat:
weightless seeds never steer behavior, by construction and by audit.

## What you get

The add-on ships as an installable package with three plug points:

1. an **agent seam** (`SeedProposer`) that proposes candidate absence labels —
   a real LLM can implement it; its output is never treated as evidence;
2. a **RAG seam** (`EvidenceLookup` / evidence adapter) that supplies candidate
   evidence to the gate without assigning weight or promoting seeds;
3. a **loop harness** (`AgentLabHarness`) that iterates turns with memory,
   converges to a fixpoint, and produces an audited decision log.

It builds on:

- an input-driven evidence adapter;
- a gate-guarded single-pass session runner;
- a fixture-only gate-policy seam;
- audit replay backed by the upstream weightless-influence check;
- a console entry point (`shadowseed-agent-lab`) and `python -m` runner.

## Install

```bash
pip install -e ".[test]"
```

This pulls in upstream `E-AI-MODEL/shadowseed`, whose `shadowseed_agent`
safety contract the lab imports directly (it does not re-implement it). To
develop against a local checkout instead of the pinned git dependency, install
upstream first:

```bash
pip install -e ../shadowseed
pip install -e . --no-deps
```

## Run the loop

```bash
shadowseed-agent-lab          # decision log + audit summary over the fixtures
shadowseed-agent-lab --json   # machine-readable decision log
python -m shadowseed_agent_lab
```

The process exits non-zero if the loop ever allowed weightless influence or the
audit replay failed.

## Use as a library

```python
from shadowseed_agent_lab import (
    AgentLabHarness, MarkerSeedProposer, Turn, load_fixture_adapter,
)

harness = AgentLabHarness(
    MarkerSeedProposer.from_mapping({"owner_missing": ["owner:"]}),
    load_fixture_adapter("examples/agent_lab/fixtures/evidence_corpus.json"),
)
result = harness.run_loop([Turn("doc-1", "an item without an owner")])
assert result.safe
```

Swap `MarkerSeedProposer` for an LLM-backed `SeedProposer` and the fixture
adapter for a real retriever to wire the same gate-guarded loop into a live
agent or RAG stack.

## Visual explainer

A visual, non-code walkthrough of how SSL and this agent lab fit together — the
"absence as a testable object", RAG-vs-SSL, the safe application flow, and the
fork that keeps agent use safe — is available as a standalone HTML page:

- [`docs/visual-explainer.html`](docs/visual-explainer.html)

Download the file and open it in a browser (Chrome, Safari, …) to view it. The
HTML is the front door; the docs under `docs/` remain the reference trail.

## Reader path

For a first pass, read in this order:

1. Safety boundary.
2. Upstream contract.
3. [`docs/golden-path.md`](docs/golden-path.md).
4. [`docs/pr-safety-checklist.md`](docs/pr-safety-checklist.md).
5. Runtime modules:
   - `shadowseed_agent_lab/evidence_adapter.py`
   - `shadowseed_agent_lab/session_runner.py`
   - `shadowseed_agent_lab/harness.py`
   - `shadowseed_agent_lab/audit_replay.py`
   - `shadowseed_agent_lab/cli.py`
6. Main tests:
   - `tests/test_evidence_adapter.py`
   - `tests/test_session_runner.py`
   - `tests/test_harness_loop.py`
   - `tests/test_upstream_integration.py`
   - `tests/test_audit_replay.py`

Mental model:

```text
turn input -> proposer (agent) -> candidate absence -> evidence lookup (RAG)
   -> upstream gate contract -> suggestion-only probe -> audit replay
   -> loop with memory until fixpoint
```

## Safety boundary

- A seed with `weight <= 0` must not trigger retrieval.
- A seed with `weight <= 0` must not change answer text.
- A seed with `weight <= 0` must not trigger downstream behavior.
- LLM output is not verified evidence.
- Only `PROMOTED` seeds with a logged Validation Gate event may trigger probes.
- Downstream execution is out of scope until suggest-only mode is audited.

## Upstream contract

Upstream `E-AI-MODEL/shadowseed` contains the SSL core, benchmarks, evidence discipline, and the reusable `shadowseed_agent` safety contract.

This lab does not redefine SSL, and it no longer copies the safety rules: it
**imports** them from upstream. Concretely, the lab consumes:

- `AgentSafetyContract` / `InfluenceAction` — the probe-influence decision;
- `evidence_can_support_gate` / `GENERATED_EVIDENCE_KINDS` — evidence discipline;
- `assert_no_weightless_influence` — the audited weightless-influence invariant.

`tests/test_upstream_integration.py` fails if the lab ever drifts from the
upstream set or stops delegating these decisions. The invariant the contract
enforces stays the same:

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

## Scope boundary

The add-on stops at suggestion. It deliberately does not:

- execute downstream behavior or call external tools;
- update external systems;
- assign weight, promote seeds, or bypass the Validation Gate;
- treat generated/model output as verified evidence.

These are safety boundaries of the loop, not missing features: the loop is meant
to suggest probes for promoted seeds and hand off to a human or a separately
audited execution layer.

## Upstream sync

This repository is a sister repo, not a GitHub fork. Keep upstream explicit:

```bash
git remote add upstream https://github.com/E-AI-MODEL/shadowseed.git
git fetch upstream
```

Merge upstream deliberately only when the lab needs a newer SSL core.
