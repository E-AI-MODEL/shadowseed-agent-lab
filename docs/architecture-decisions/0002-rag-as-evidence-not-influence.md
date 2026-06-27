# 0002: RAG Is Evidence, Not Influence

## Status

Accepted.

## Context

The lab will add RAG-style retrieval experiments. Without a clear boundary, retrieval could accidentally become a second promotion path for seeds.

That would violate the upstream SSL rule that weight is influence and that weight may rise only through validation.

## Decision

RAG is an evidence provider, not an influence authority.

RAG may:

- retrieve candidate evidence;
- attach evidence references;
- mark evidence as verified or unverified through an adapter;
- pass evidence references to the Validation Gate.

RAG may not:

- assign seed weight;
- promote a seed;
- bypass the Validation Gate;
- let a weightless seed steer retrieval or answer text.

## Golden path

```text
seed candidate
  -> weightless seed
  -> evidence lookup
  -> verified evidence refs
  -> Validation Gate
  -> promoted seed
  -> bounded probe suggestion
  -> decision log
```

## Blocked path

```text
weightless seed
  -> retrieval steering
  -> answer change
```

## Consequences

The evidence adapter must keep generated model output separate from verified evidence.

The session runner must require a positive-weight, promoted, gate-logged seed before allowing probe suggestions or other agent-side influence.

Tests must include at least one blocked weightless seed and one promoted gate-backed seed.
