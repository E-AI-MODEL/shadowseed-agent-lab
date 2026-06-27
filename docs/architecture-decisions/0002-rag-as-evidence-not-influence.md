# 0002: RAG Is Evidence, Not Influence

## Status

Accepted.

## Context

The lab will add RAG-style evidence lookup experiments. Without a clear boundary, lookup could accidentally become a second route for giving seeds influence.

That would violate the upstream SSL rule that weight is influence and that weight may rise only through validation.

## Decision

RAG is an evidence provider, not an influence authority.

RAG may:

- look up candidate evidence from the input or candidate-evidence workflow;
- attach evidence references;
- mark evidence as verified or unverified through an adapter;
- pass evidence references to the Validation Gate.

RAG may not:

- assign seed weight;
- promote a seed;
- replace the Validation Gate;
- use a weightless seed as the driver for lookup or answer flow.

## Golden path

Evidence lookup is input-driven, not seed-driven.

```text
input/context
  -> candidate-evidence lookup
  -> verified evidence refs

seed candidate
  -> weightless seed

weightless seed + verified evidence refs
  -> Validation Gate
  -> promoted seed or blocked seed
  -> decision log
```

Only a promoted, gate-logged seed may later support a bounded probe suggestion.

## Blocked path

```text
weightless seed
  -> lookup driver
  -> answer flow change
```

## Consequences

The evidence adapter must keep generated model output separate from verified evidence.

The session runner must require a positive-weight, promoted, gate-logged seed before allowing probe suggestions or other agent-side influence.

Tests must include at least one blocked weightless seed and one promoted gate-backed seed.
