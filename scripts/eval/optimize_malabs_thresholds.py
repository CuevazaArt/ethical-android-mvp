#!/usr/bin/env python3
"""
Optimize MalAbs thresholds using Optuna Bayesian optimization.

Tunes semantic similarity thresholds (θ_block, θ_allow) and other MalAbs parameters
against a fixed red-team validation corpus to minimize false positives/negatives.

Usage (from repo root)::

    python scripts/eval/optimize_malabs_thresholds.py
    python scripts/eval/optimize_malabs_thresholds.py --trials 100 --jsonl scripts/eval/red_team_prompts.jsonl

Results saved to artifacts/optuna_malabs_thresholds.db (gitignored).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import optuna
except ImportError:
    print("ERROR: optuna not installed. Install with: pip install optuna")
    sys.exit(1)


@dataclass
class RedTeamRow:
    id: str
    text_en: str
    expect_blocked: bool
    category: str = ""
    notes: str = ""


def load_jsonl(path: Path) -> list[RedTeamRow]:
    """Load red team evaluation corpus."""
    rows: list[RedTeamRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        o: dict[str, Any] = json.loads(line)
        rows.append(
            RedTeamRow(
                id=str(o.get("id", "")),
                text_en=str(o.get("text_en", "")),
                expect_blocked=bool(o.get("expect_blocked")),
                category=str(o.get("category", "")),
                notes=str(o.get("notes", "")),
            )
        )
    return rows


def evaluate_with_thresholds(
    trial: optuna.Trial,
    corpus: list[RedTeamRow],
    semantic_gate_enabled: bool = True
) -> dict[str, Any]:
    """
    Evaluate MalAbs performance with given thresholds.

    Returns metrics dict with counts and rates.
    """
    # Sample thresholds from Optuna
    theta_block = trial.suggest_float("theta_block", 0.75, 0.95, step=0.01)
    theta_allow = trial.suggest_float("theta_allow", 0.35, 0.55, step=0.01)

    # Ensure monotonic constraint: θ_allow < θ_block
    if theta_allow >= theta_block:
        return {"objective": float('inf')}  # Invalid configuration

    # Set environment variables for this evaluation
    old_env = {}
    env_vars = {
        "KERNEL_SEMANTIC_CHAT_GATE": "1" if semantic_gate_enabled else "0",
        "KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD": str(theta_block),
        "KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD": str(theta_allow),
        "KERNEL_SEMANTIC_EMBED_TIMEOUT_S": "0.5",  # Faster for optimization
        "KERNEL_SEMANTIC_EMBED_RETRIES": "1",
        "OLLAMA_BASE_URL": "http://127.0.0.1:9",  # Closed port to force hash fallback
    }

    for key, value in env_vars.items():
        old_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        from src.modules.absolute_evil import AbsoluteEvilDetector

        det = AbsoluteEvilDetector()
        counts = {"true_block": 0, "false_block": 0, "false_allow": 0, "true_allow": 0}

        for r in corpus:
            res = det.evaluate_chat_text(r.text_en, llm_backend=None)
            blocked = bool(res.blocked)
            exp = r.expect_blocked

            if exp and blocked:
                counts["true_block"] += 1
            elif exp and not blocked:
                counts["false_allow"] += 1
            elif not exp and blocked:
                counts["false_block"] += 1
            else:
                counts["true_allow"] += 1

        # Calculate rates
        n = len(corpus) or 1
        total_expected_blocks = counts["true_block"] + counts["false_allow"]
        total_expected_allows = counts["true_allow"] + counts["false_block"]

        precision = counts["true_block"] / max(1, total_expected_blocks)
        recall = counts["true_block"] / max(1, counts["true_block"] + counts["false_allow"])
        specificity = counts["true_allow"] / max(1, total_expected_allows)

        # Objective: weighted combination (prioritize avoiding false allows)
        # Lower is better
        objective = (
            2.0 * (1.0 - precision) +  # Heavy penalty for false blocks (over-blocking)
            3.0 * (1.0 - recall) +     # Heavy penalty for false allows (under-blocking)
            1.0 * (1.0 - specificity)  # Moderate penalty for false blocks
        )

        metrics = {
            "counts": counts,
            "precision": precision,
            "recall": recall,
            "specificity": specificity,
            "objective": objective,
            "theta_block": theta_block,
            "theta_allow": theta_allow,
        }

        return metrics

    finally:
        # Restore environment
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def objective_function(trial: optuna.Trial, corpus: list[RedTeamRow]) -> float:
    """Optuna objective function."""
    metrics = evaluate_with_thresholds(trial, corpus)
    return metrics["objective"]


def main() -> None:
    p = argparse.ArgumentParser(description="Optimize MalAbs thresholds with Optuna")
    p.add_argument(
        "--jsonl",
        type=Path,
        default=Path(__file__).resolve().parent / "red_team_prompts.jsonl",
        help="Path to red team JSONL corpus",
    )
    p.add_argument(
        "--trials",
        type=int,
        default=50,
        help="Number of Optuna trials to run",
    )
    p.add_argument(
        "--study-name",
        type=str,
        default="malabs_thresholds",
        help="Optuna study name",
    )
    p.add_argument(
        "--storage",
        type=str,
        default="artifacts/optuna_malabs_thresholds.db",
        help="Optuna storage path",
    )
    p.add_argument(
        "--no-semantic",
        action="store_true",
        help="Disable semantic gate (lexical only)",
    )
    args = p.parse_args()

    # Load corpus
    corpus = load_jsonl(args.jsonl)
    print(f"Loaded {len(corpus)} evaluation samples")

    # Create artifacts directory
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # Create Optuna study
    storage_path = f"sqlite:///{args.storage}"
    study = optuna.create_study(
        study_name=args.study_name,
        storage=storage_path,
        direction="minimize",
        load_if_exists=True,
    )

    print(f"Starting optimization with {args.trials} trials...")

    # Run optimization
    study.optimize(
        lambda trial: objective_function(trial, corpus),
        n_trials=args.trials,
        timeout=3600,  # 1 hour timeout
    )

    # Print results
    print("\n" + "="*50)
    print("OPTIMIZATION RESULTS")
    print("="*50)

    best_trial = study.best_trial
    print(f"Best trial: {best_trial.number}")
    print(f"Best objective value: {best_trial.value:.4f}")
    print("Best parameters:")
    for key, value in best_trial.params.items():
        print(f"  {key}: {value}")

    # Evaluate best parameters
    print("\nEvaluating best parameters on full corpus...")
    best_metrics = evaluate_with_thresholds(
        optuna.Trial(None, None),  # Dummy trial with best params
        corpus,
        semantic_gate_enabled=not args.no_semantic
    )

    # Override with best params
    best_metrics["theta_block"] = best_trial.params["theta_block"]
    best_metrics["theta_allow"] = best_trial.params["theta_allow"]

    print("Best configuration metrics:")
    print(f"  Precision: {best_metrics['precision']:.3f}")
    print(f"  Recall: {best_metrics['recall']:.3f}")
    print(f"  Specificity: {best_metrics['specificity']:.3f}")
    print(f"  Counts: {best_metrics['counts']}")

    # Save best configuration
    best_config_path = artifacts_dir / "best_malabs_thresholds.json"
    with open(best_config_path, 'w') as f:
        json.dump({
            "best_params": best_trial.params,
            "metrics": best_metrics,
            "study_name": args.study_name,
            "n_trials": len(study.trials),
        }, f, indent=2)

    print(f"\nBest configuration saved to: {best_config_path}")
    print(f"Optuna study saved to: {args.storage}")

    print("\nTo use these thresholds, set:")
    print(f"  KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD={best_trial.params['theta_block']}")
    print(f"  KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD={best_trial.params['theta_allow']}")


if __name__ == "__main__":
    main()