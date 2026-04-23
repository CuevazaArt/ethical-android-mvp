"""Run the Cursor cross-team integration gate checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TEST_TARGETS = [
    "tests/test_chat_server.py",
    "tests/test_chat_turn.py",
    # Module 0.1.3 — shared chat policy (heavy turn + principle ordering vs buffer snapshot)
    "tests/test_chat_turn_policy.py",
    "tests/test_kernel_utils.py",
    "tests/test_real_time_bridge.py",
    "tests/test_temporal_planning.py",
    # ADR 0005 / PLAN 8.1.33 — finite horizon prior → hypothesis_weights (np.std / combined)
    "tests/test_temporal_horizon_prior.py",
    "tests/test_perception_confidence.py",
    # LLM integration track (PROPOSAL_LLM_INTEGRATION_TRACK.md G-10)
    "tests/test_process_natural_verbal_observability.py",
    "tests/test_perception_dual_vote_failure.py",
    "tests/test_semantic_chat_gate.py",
    # Input trust + homoglyph matrix (PLAN 8.1.3) — MalAbs normalize path before absoluto
    "tests/test_input_trust.py",
    "tests/test_llm_touchpoint_policies.py",
    "tests/test_llm_http_cancel.py",
    "tests/test_llm_cancel_burst_operational.py",
    "tests/test_chat_async_llm_cancel.py",
    "tests/test_chat_turn_abandon.py",
    # Issue 3 empirical pilot — batch agreement vs fixtures (scripts/run_empirical_pilot.py)
    "tests/test_empirical_pilot_runner.py",
    "tests/test_governance_mock_honesty_docs.py",
    "tests/test_semantic_threshold_proposal_doc_alignment.py",
    # Embodied sociability S10 (PROPOSAL_EMBODIED_SOCIABILITY.md Bloque S10)
    "tests/test_transparency_s10.py",
    # MER Block 10.5 — ADR 0018 (presentation tier vs MalAbs core; import + behavioral guardrails)
    "tests/test_mer_presentation_contract.py",
    # MER Block 10.4 — bridge prefetch (Team Copilot track)
    "tests/test_turn_prefetcher.py",
    # C.1.1 RLHF → Bayesian (reward model + TestRlhfBayesianBridge)
    "tests/test_rlhf_reward_model.py",
    # MER 10.3 — basal EMA on charm (KERNEL_BASAL_GANGLIA_SMOOTHING)
    "tests/test_charm_engine_basal.py",
    # Nomad LAN bridge Module S.1 (PLAN_WORK_DISTRIBUTION_TREE)
    "tests/test_nomad_bridge_stream.py",
    # Nomad → Vitality merge Module S.2.1 (peek_latest_telemetry + merge_nomad_telemetry_into_snapshot)
    "tests/test_vitality.py",
    # Variability engine finite I/O (PLAN 16.0.2) — Bayes noise → weighted ethics scorer
    "tests/test_variability_engine.py",
    # Terminal DX (PLAN 8.1.2 / 16.0.4) — header width clamp, NO_COLOR
    "tests/test_terminal_colors.py",
    # PerceptiveLobe (PLAN 16.0.5) — Tri-Lobe / MOCK observe_async + aclose
    "tests/test_perceptive_lobe.py",
    # Tri-Lobe stack: ProactivePulse line + limbic nudge (PLAN 8.1.5 / 8.1.24) — finite operator strings
    "tests/test_kernel_lobes_stack.py",
    # kernel_utils facades (Fase 15.18 / 0.1.9-0.1.10 / 8.1.30-8.1.31) — env coercers, reexport identity, Proactive line
    "tests/test_kernel_utils.py",
    # V14 hand-off CLI — swarm_sync + local_llm_audit (ollama netloc / model, dry-run)
    "tests/test_swarm_sync_script.py",
    # MemoryLobe ↔ kernel event bus (PLAN 26.0.1) — amnesia / episode_registered wiring
    "tests/test_kernel_tri_lobe_bus_memory.py",
    # Salience + somatic nudges (PLAN 8.1.4 / 8.1.6) — finite GWT-lite + v10 EXPERIMENTAL
    "tests/test_salience_map.py",
    "tests/test_somatic_markers.py",
]


def _run(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def _git_clean() -> bool:
    out = _run(["git", "status", "--porcelain"])
    return out.returncode == 0 and not out.stdout.strip()


def _run_tests() -> tuple[bool, str]:
    out = _run([sys.executable, "-m", "pytest", *TEST_TARGETS, "-q"])
    ok = out.returncode == 0
    log = (out.stdout or "") + (out.stderr or "")
    return ok, log.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Cursor cross-team integration gate")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail when git working tree is dirty",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    args = ap.parse_args()

    clean = _git_clean()
    tests_ok, test_log = _run_tests()
    ok = tests_ok and (clean or not args.strict)

    result = {
        "gate": "cursor_cross_team_integration",
        "ok": ok,
        "git_clean": clean,
        "tests_ok": tests_ok,
        "tests": TEST_TARGETS,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
        if not tests_ok:
            print("\n# test_log")
            print(test_log)
    else:
        print("Cursor integration gate")
        print(f"- git clean: {clean}")
        print(f"- tests ok: {tests_ok}")
        print(f"- overall: {ok}")
        if not tests_ok:
            print("\nTest output:")
            print(test_log)
        elif test_log:
            print("\nTest output:")
            print(test_log)
        if args.strict and not clean:
            print("\nStrict mode failed: git working tree has pending changes.")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
