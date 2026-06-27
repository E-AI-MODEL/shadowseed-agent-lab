# Agent Lab Review Checklist

Use this checklist for PRs in `E-AI-MODEL/shadowseed-agent-lab`.

## Before editing

- Check open PRs and issues.
- Read Codex review threads, not just regular comments.
- Verify whether previous PRs are merged before stacking or retargeting.

## Input and evidence

- Evidence lookup must start from input/context, not from a seed object.
- Normalized-empty candidates must not reach seed creation.
- Unlabeled evidence must not match every request.
- Unrelated verified evidence must not support a seed.
- Generated/model output must not count as trusted evidence.

## Influence and probes

- A seed with `weight <= 0` must not influence retrieval, probes, answer text, warnings, tool calls, or decisions.
- Probes must remain suggestion-only.
- Allowed influence must require a promoted, gate-logged seed.
- The decision seed, session seed, gate seed, and gate reference must match.

## Fixture policy

- Fixture policies must be named as fixture-only.
- Fixture policies must not be presented as upstream SSL semantics.
- Prefer injected policy seams when behavior could drift into upstream-owned meaning.

## Audit and tests

- Add regression tests for every discovered invariant bug.
- Add replay checks for allowed decisions.
- Run or document the local test gate:

```bash
python -m unittest discover -s tests
```

## Reporting

Report:

- PR number and status;
- unresolved Codex comments;
- files changed;
- tests added;
- blockers;
- next recommended PR.
