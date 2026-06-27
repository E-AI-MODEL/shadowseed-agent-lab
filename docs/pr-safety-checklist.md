# PR Safety Checklist

Use this checklist for every agent-lab pull request.

## Upstream alignment

- Does the PR treat `E-AI-MODEL/shadowseed` as the source for SSL semantics?
- Does the PR avoid redefining seed lifecycle, promotion, trace/weight behavior, or Validation Gate meaning?
- If a fixture policy is used, is it named as fixture-only?

## Input and lookup boundary

- Does evidence lookup start from input/context rather than from a seed object?
- Can a normalized-empty candidate reach seed creation or gate logic?
- Can unlabeled evidence match broadly?
- Can unrelated verified evidence support a seed?
- Can generated/model output count as trusted evidence?

## Influence boundary

- Can a seed with `weight <= 0` steer retrieval, probes, answer text, warnings, or decisions?
- Is probe output suggestion-only?
- Is every allowed seed-driven decision tied to a promoted, gate-logged seed?
- Is every decision logged in a replayable form?

## Test gate

Before merge, run:

```bash
python -m unittest discover -s tests
```

Record the result in the PR body or review comment.
