---
name: shadowseed-agent-lab
description: Use this skill when reviewing, extending, or packaging the Shadowseed agent lab. Apply it for PR planning, Codex review triage, SSL upstream alignment checks, agent/RAG boundary reviews, fixture-policy drift checks, audit replay checks, and creation of small follow-up PRs in E-AI-MODEL/shadowseed-agent-lab. The skill treats E-AI-MODEL/shadowseed as the source of SSL semantics and keeps this lab in research/prototype mode.
---

# Shadowseed Agent Lab Skill

## Use when

Use this skill for work on `E-AI-MODEL/shadowseed-agent-lab`, especially:

- reviewing or creating PRs;
- handling Codex review comments;
- checking alignment with upstream `E-AI-MODEL/shadowseed`;
- adding agent/RAG integration behavior;
- updating fixtures, evidence adapters, session runners, audit replay, or policy seams;
- deciding whether a change belongs in the lab repo or upstream SSL repo.

## Hard boundary

`E-AI-MODEL/shadowseed` is the source of SSL semantics.

The lab repo may:

- add agent/RAG integration experiments;
- use input-driven evidence lookup;
- create fixture-only policies;
- add suggestion-only probes;
- add audit replay checks;
- package reviewer/agent workflows.

The lab repo must not redefine:

- seed lifecycle;
- trace/weight behavior;
- Validation Gate meaning;
- contradiction handling;
- promotion semantics;
- evidence discipline;
- production-readiness claims.

## Core invariants

Always preserve:

```text
trace > 0 means the seed is present
weight = 0 means the seed does not steer
```

Agent boundary:

```text
weight <= 0 must not drive retrieval, probes, answer text, warnings, tool calls, or decisions
only promoted, gate-logged seeds may influence suggestion-only probes
generated/model output is not verified evidence
```

## PR workflow

1. Inspect current PR state, review threads, and open issues before making changes.
2. Read relevant files on the branch before editing.
3. Keep PRs small and focused.
4. Fix Codex review comments in the current PR before opening the next behavior PR.
5. Add tests for every invariant bug.
6. Reply to the review comment with the code and test coverage summary.
7. Resolve the thread only after code and tests are present.
8. Do not update README until the end-of-phase status pass.

## Review checklist

Load `references/review-checklist.md` when reviewing a PR or Codex comment.

Load `references/upstream-contract.md` when deciding whether behavior belongs in the lab repo or upstream SSL repo.

## Expected output style

When reporting status, include:

- PR number and state;
- relevant Codex comments and whether they are resolved;
- exact files changed;
- remaining blockers;
- recommended next PR.

Do not claim production readiness. Use research/prototype language unless upstream evidence supports a stronger claim.
