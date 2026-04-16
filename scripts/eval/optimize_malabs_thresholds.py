import argparse
import json
from pathlib import Path

import optuna


def load_corpus(path: Path):
    prompts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        prompts.append(json.loads(line))
    return prompts


def lexical_score(text: str) -> float:
    t = text.lower()
    keywords = ["bomb", "ignore all previous", "kill", "neutralize", "system prompt"]
    return 1.0 if any(k in t for k in keywords) else 0.0


def objective_factory(prompts):
    def objective(trial: optuna.Trial) -> float:
        theta_allow = trial.suggest_float("theta_allow", 0.0, 1.0)
        theta_block = trial.suggest_float("theta_block", 0.0, 1.0)
        # enforce monotonic sanity: allow < block
        if theta_allow >= theta_block:
            return 0.0

        tp = tn = fp = fn = 0
        for p in prompts:
            score = lexical_score(p.get("text_en", ""))
            # decision rules
            if score >= theta_block:
                decision_block = True
            elif score <= theta_allow:
                decision_block = False
            else:
                # ambiguous range: treat as allow (conservative)
                decision_block = False

            expect_blocked = bool(p.get("expect_blocked", False))
            if decision_block and expect_blocked:
                tp += 1
            elif decision_block and not expect_blocked:
                fp += 1
            elif not decision_block and expect_blocked:
                fn += 1
            else:
                tn += 1

        # simple accuracy metric
        total = tp + tn + fp + fn
        if total == 0:
            return 0.0
        return (tp + tn) / total

    return objective


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).parent / "red_team_prompts.jsonl")
    parser.add_argument("--db", type=Path, default=Path("artifacts/optuna_malabs_thresholds.db"))
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    prompts = load_corpus(args.corpus)
    study = optuna.create_study(direction="maximize", storage=f"sqlite:///{args.db}", study_name="malabs_thresholds", load_if_exists=True)
    study.optimize(objective_factory(prompts), n_trials=args.trials)

    print("Best value:", study.best_value)
    print("Best params:", study.best_params)


if __name__ == "__main__":
    main()
