# Agent Lab Examples

This directory contains fixture-driven demos for the Shadow Seed Learning agent lab.

The first examples should stay deterministic:

- no live model requirement;
- no external action execution;
- no production claims;
- clear decision logs.

## Planned demo

```text
school_notes_demo.py
fixtures/
  meeting_notes.md
  policy_action_points.md
```

The demo should show:

1. seed candidate detected;
2. seed starts weightless;
3. evidence is checked separately;
4. Validation Gate blocks or promotes;
5. only promoted seeds may suggest a probe;
6. audit replay passes.

## Expected console shape

```text
seed_detected: owner_missing
seed_weight: 0.0
gate: blocked
probe: none
audit: passed

seed_detected: deadline_missing
seed_weight: 0.6
gate: promoted
probe: ask_for_deadline
audit: passed
```
