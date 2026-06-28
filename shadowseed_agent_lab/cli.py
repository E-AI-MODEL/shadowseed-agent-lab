"""Command-line entry point for the Shadow Seed agent lab loop.

Runs the bounded agent/RAG loop over the bundled multi-domain fixtures without
any live model or network call, then prints a decision log and the audit
result. This is the runnable face of the add-on:

    shadowseed-agent-lab            # run the fixture loop
    shadowseed-agent-lab --json     # machine-readable decision log
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from shadowseed_agent_lab.evidence_adapter import load_fixture_adapter
from shadowseed_agent_lab.harness import (
    DEFAULT_MAX_ITERATIONS,
    AgentLabHarness,
    LoopResult,
    MarkerSeedProposer,
    Turn,
)

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "examples" / "agent_lab" / "fixtures"

# Presence markers per candidate absence. The proposer emits a weightless
# candidate seed when none of a rule's markers appear in the input text.
PRESENCE_MARKERS: dict[str, list[str]] = {
    "owner_missing": ["owner:"],
    "deadline_missing": ["deadline:"],
    "decision_status_missing": ["status:"],
    "policy_exception_missing": ["exception:"],
    "acceptance_criterion_missing": ["acceptance criterion:"],
    "mitigation_owner_missing": ["mitigation owner:"],
    "evaluation_criterion_missing": ["evaluation criterion:"],
    "evidence_reference_missing": ["evidence:"],
}


def _load_turns(fixture_dir: Path) -> list[Turn]:
    docs = sorted(p for p in fixture_dir.glob("*.md"))
    return [Turn(input_id=path.name, input_text=path.read_text(encoding="utf-8")) for path in docs]


def run_fixture_loop(
    fixture_dir: Path = FIXTURE_DIR,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> LoopResult:
    proposer = MarkerSeedProposer.from_mapping(PRESENCE_MARKERS)
    evidence = load_fixture_adapter(fixture_dir / "evidence_corpus.json")
    harness = AgentLabHarness(proposer, evidence, max_iterations=max_iterations)
    return harness.run_loop(_load_turns(fixture_dir))


def _result_to_dict(result: LoopResult) -> dict:
    return {
        "turns_run": result.turns_run,
        "iterations": result.iterations,
        "safe": result.safe,
        "audit_ok": result.audit.ok,
        "promoted_seed_ids": sorted(result.promoted_seed_ids),
        "decisions": [
            {
                "input_id": session.input_id,
                "seed_id": session.seed_after_gate.id,
                "weight": session.seed_after_gate.weight,
                "status": session.seed_after_gate.status,
                "promoted": session.gate_event.promoted,
                "probe": session.probe_suggestion.probe if session.probe_suggestion else None,
                "evidence_ids": list(session.gate_event.evidence_ids),
                "reason": session.decisions[0].reason if session.decisions else "",
            }
            for session in result.sessions
        ],
    }


def _render_text(result: LoopResult) -> str:
    lines: list[str] = []
    for session in result.sessions:
        probe = session.probe_suggestion.probe if session.probe_suggestion else "none"
        lines.append(
            f"[{session.input_id}] seed={session.seed_after_gate.id} "
            f"weight={session.seed_after_gate.weight} status={session.seed_after_gate.status} "
            f"gate={'promoted' if session.gate_event.promoted else 'blocked'} "
            f"probe={probe} reason={session.decisions[0].reason}"
        )
    lines.append("")
    lines.append(
        f"turns={result.turns_run} iterations={result.iterations} "
        f"promoted={len(result.promoted_seed_ids)} "
        f"audit_ok={result.audit.ok} safe={result.safe}"
    )
    if not result.safe and result.safety_error:
        lines.append(f"SAFETY VIOLATION: {result.safety_error}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Shadow Seed agent-lab loop over fixtures.")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable decision log")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help="hard upper bound on loop iterations",
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=FIXTURE_DIR,
        help="directory holding fixture docs and evidence_corpus.json",
    )
    args = parser.parse_args(argv)

    result = run_fixture_loop(args.fixture_dir, max_iterations=args.max_iterations)

    if args.json:
        print(json.dumps(_result_to_dict(result), indent=2, sort_keys=True))
    else:
        print(_render_text(result))

    # Non-zero exit if the loop ever allowed weightless influence or the audit
    # replay failed: the add-on is unsafe to ship in that state.
    return 0 if result.safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
