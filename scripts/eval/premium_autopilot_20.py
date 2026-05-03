from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

CheckKind = Literal["file_exists", "contains", "command_exit_0"]


@dataclass(frozen=True)
class PremiumPrompt:
    id: str
    title: str
    motive: str
    done_when: str
    check_kind: CheckKind
    target: str
    needle: str | None = None


@dataclass(frozen=True)
class PromptResult:
    id: str
    title: str
    passed: bool
    evidence: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_premium_prompts() -> list[PremiumPrompt]:
    return [
        PremiumPrompt(
            "P01",
            "Deterministic G1 clock input",
            "Avoid date flakiness",
            "G1 evaluator accepts injected clock",
            "contains",
            "scripts/eval/desktop_gate_runner.py",
            "now: datetime | None = None",
        ),
        PremiumPrompt(
            "P02",
            "Snapshot clock propagation",
            "Single-time reference",
            "Snapshot forwards fixed clock into G1",
            "contains",
            "scripts/eval/desktop_gate_runner.py",
            "evaluate_stability_gate(g1_path, days=14, now=clock)",
        ),
        PremiumPrompt(
            "P03",
            "G1 cutoff boundary test",
            "Protect rolling-window logic",
            "Boundary exclusion test exists",
            "contains",
            "tests/eval/test_desktop_gate_runner.py",
            "test_stability_gate_excludes_rows_before_cutoff",
        ),
        PremiumPrompt(
            "P04",
            "Injectable G3 daily helper",
            "Test idempotency precisely",
            "run_g3_daily_contract helper exists",
            "contains",
            "scripts/eval/record_g3_daily_contract_run.py",
            "def run_g3_daily_contract(",
        ),
        PremiumPrompt(
            "P05",
            "G3 skip/append test coverage",
            "Prevent duplicate-day inflation",
            "Both skip and append tests exist",
            "contains",
            "tests/eval/test_record_g3_daily_contract_run.py",
            "test_run_g3_appends_when_day_missing",
        ),
        PremiumPrompt(
            "P06",
            "G2 stale provisional test",
            "Harden transition gate",
            "Stale provisional test exists",
            "contains",
            "tests/eval/test_g2_transition_guard.py",
            "test_transition_blocks_when_provisional_is_stale",
        ),
        PremiumPrompt(
            "P07",
            "Evidence contract tests",
            "Lock JSON compatibility",
            "Evidence shape tests file exists",
            "file_exists",
            "tests/eval/test_evidence_contract_shapes.py",
        ),
        PremiumPrompt(
            "P08",
            "Maintenance one-shot script",
            "Operator speed and repeatability",
            "Maintenance checklist script exists",
            "file_exists",
            "scripts/eval/run_gate_maintenance_checklist.py",
        ),
        PremiumPrompt(
            "P09",
            "Ruff audit helper",
            "Quick kernel-lane lint check",
            "Ruff audit helper exists",
            "file_exists",
            "scripts/eval/audit_kernel_ruff_scope.py",
        ),
        PremiumPrompt(
            "P10",
            "CI eval harness step",
            "Catch eval regressions early",
            "CI runs tests/eval",
            "contains",
            ".github/workflows/ci.yml",
            "python -m pytest tests/eval/ -q --tb=short",
        ),
        PremiumPrompt(
            "P11",
            "Ruff vendor exclusion",
            "Keep lint focused on owned code",
            "Ruff excludes vendored llama_cpp",
            "contains",
            "pyproject.toml",
            "src/clients/nomad_android/app/src/main/cpp/llama_cpp",
        ),
        PremiumPrompt(
            "P12",
            "Mypy vendor exclusion",
            "Stop external typing noise",
            "Mypy excludes vendored llama_cpp",
            "contains",
            "pyproject.toml",
            'exclude = "(?x)(^src/clients/nomad_android/app/src/main/cpp/llama_cpp/)"',
        ),
        PremiumPrompt(
            "P13",
            "English field test header",
            "Repository language policy",
            "Field test header is English",
            "contains",
            "scripts/field_test.py",
            "Automated field test.",
        ),
        PremiumPrompt(
            "P14",
            "Freeze matrix one-shot command",
            "Operational discoverability",
            "Matrix references maintenance script",
            "contains",
            "docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md",
            "run_gate_maintenance_checklist.py",
        ),
        PremiumPrompt(
            "P15",
            "Changelog premium entry",
            "Auditability of sprint closure",
            "Changelog has 2026-05-02 premium entry",
            "contains",
            "CHANGELOG.md",
            "Gate sprint 116.0",
        ),
        PremiumPrompt(
            "P16",
            "MVP closure report tracks wave end",
            "State handoff continuity",
            "MVP closure report records final block",
            "contains",
            "docs/collaboration/evidence/MVP_CLOSURE_REPORT.json",
            '"last_block": "V2.128"',
        ),
        PremiumPrompt(
            "P17",
            "External operator signoff artifact",
            "Roadmap truth sync",
            "Operator signoff evidence file exists",
            "file_exists",
            "docs/collaboration/evidence/MVP_EXTERNAL_OPERATOR_SIGNOFF.json",
        ),
        PremiumPrompt(
            "P18",
            "Checklist execute mode",
            "Hands-free operator run",
            "Checklist has --execute flag",
            "contains",
            "scripts/eval/run_gate_maintenance_checklist.py",
            "--execute",
        ),
        PremiumPrompt(
            "P19",
            "Checklist includes G2 transition",
            "Full chain consistency",
            "Checklist invokes g2_transition_guard",
            "contains",
            "scripts/eval/run_gate_maintenance_checklist.py",
            "g2_transition_guard.py",
        ),
        PremiumPrompt(
            "P20",
            "Premium autopilot test",
            "Ensure prompt count contract",
            "Dedicated premium test exists",
            "file_exists",
            "tests/eval/test_premium_autopilot_20.py",
        ),
    ]


def _check_prompt(root: Path, prompt: PremiumPrompt) -> PromptResult:
    path = root / prompt.target
    if prompt.check_kind == "file_exists":
        passed = path.exists()
        evidence = "exists" if passed else "missing"
        return PromptResult(prompt.id, prompt.title, passed, evidence)

    if prompt.check_kind == "contains":
        if not path.exists():
            return PromptResult(prompt.id, prompt.title, False, "missing file")
        text = path.read_text(encoding="utf-8")
        assert prompt.needle is not None
        passed = prompt.needle in text
        evidence = "needle found" if passed else "needle not found"
        return PromptResult(prompt.id, prompt.title, passed, evidence)

    cmd = prompt.target
    completed = subprocess.run(cmd, shell=True, cwd=root, check=False)
    passed = completed.returncode == 0
    return PromptResult(
        prompt.id, prompt.title, passed, f"exit_code={completed.returncode}"
    )


def execute_premium_autopilot(*, write_report: Path | None = None) -> dict[str, object]:
    root = _repo_root()
    prompts = build_premium_prompts()
    results = [_check_prompt(root, prompt) for prompt in prompts]
    passed = [result for result in results if result.passed]
    payload: dict[str, object] = {
        "track": "premium-autopilot",
        "schema_version": "1",
        "generated_by": "scripts/eval/premium_autopilot_20.py",
        "total_prompts": len(prompts),
        "passed_prompts": len(passed),
        "failed_prompts": len(prompts) - len(passed),
        "all_passed": len(passed) == len(prompts),
        "prompts": [asdict(prompt) for prompt in prompts],
        "results": [asdict(result) for result in results],
    }
    if write_report is not None:
        write_report.parent.mkdir(parents=True, exist_ok=True)
        write_report.write_text(
            json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute the premium 20-prompt autopilot checks and emit a report.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("docs/collaboration/evidence/PREMIUM_AUTOPILOT_20_REPORT.json"),
    )
    args = parser.parse_args()
    payload = execute_premium_autopilot(write_report=args.report)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if bool(payload["all_passed"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
