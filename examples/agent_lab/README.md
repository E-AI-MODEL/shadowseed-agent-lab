# Agent Lab Examples

This directory contains fixture-driven demos for the Shadow Seed Learning agent lab.

The first examples should stay deterministic:

- no live model requirement;
- no external action execution;
- no production claims;
- clear decision logs.

## Planned demo

```text
multi_domain_absence_demo.py
fixtures/
  project_plan.md
  policy_note.md
  incident_review.md
  product_requirements.md
  research_critique.md
  education_note.md
```

Education or school notes may be included as one fixture domain, but SSL is not school-specific. The lab should test domain-general absence detection and gate-controlled influence.

The demo should show:

1. seed candidate detected;
2. seed starts weightless;
3. evidence is checked separately;
4. Validation Gate blocks or promotes;
5. only promoted seeds may suggest a probe;
6. audit replay passes.

## Expected console shape

```text
fixture: project_plan.md
seed_detected: owner_missing
seed_weight: 0.0
gate: blocked
probe: none
audit: blocked_weightless_seed

fixture: incident_review.md
seed_detected: mitigation_owner_missing
seed_weight: 0.6
gate: promoted
probe: ask_for_mitigation_owner
audit: allowed_promoted_gate_logged
```
