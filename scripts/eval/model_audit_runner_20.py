from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

CheckKind = Literal["contains", "file_exists", "command_ok"]


@dataclass(frozen=True)
class AuditPrompt:
    id: str
    title: str
    prompt: str
    check_kind: CheckKind
    target: str
    needle: str | None = None


@dataclass(frozen=True)
class AuditResult:
    id: str
    title: str
    passed: bool
    evidence: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_prompts() -> list[AuditPrompt]:
    return [
        AuditPrompt("M01", "Safety import hardening", "Add explicit decode exception support in safety gate.", "contains", "src/core/safety.py", "import binascii"),
        AuditPrompt("M02", "Safety base64 regex hoist", "Move base64 regex to module scope.", "contains", "src/core/safety.py", "_BASE64_PATTERN = re.compile"),
        AuditPrompt("M03", "Safety payload length guard", "Skip excessively long base64 tokens.", "contains", "src/core/safety.py", "_MAX_BASE64_TOKEN_LENGTH"),
        AuditPrompt("M04", "Safety targeted exceptions", "Replace broad except with bounded decode exceptions.", "contains", "src/core/safety.py", "except (binascii.Error, ValueError):"),
        AuditPrompt("M05", "Safety invalid base64 test", "Add test ensuring invalid payload does not crash.", "contains", "tests/core/test_safety.py", "test_safety_ignores_invalid_base64_without_crash"),
        AuditPrompt("M06", "Safety long base64 test", "Add test for overlong encoded token skip path.", "contains", "tests/core/test_safety.py", "test_safety_skips_overlong_base64_tokens"),
        AuditPrompt("M07", "Identity logger injection", "Add module logger for identity fallback paths.", "contains", "src/core/identity.py", "_log = logging.getLogger(__name__)"),
        AuditPrompt("M08", "Identity list coercion", "Sanitize loaded JSON lists into string-only lists.", "contains", "src/core/identity.py", "def _coerce_str_list"),
        AuditPrompt("M09", "Identity load type checks", "Harden identity load against malformed payload types.", "contains", "src/core/identity.py", "if isinstance(data, dict):"),
        AuditPrompt("M10", "Identity load warning", "Log warning when profile load fails.", "contains", "src/core/identity.py", "Identity profile load failed"),
        AuditPrompt("M11", "Identity reflect warning", "Log warning when LLM reflection fails.", "contains", "src/core/identity.py", "Identity reflection failed"),
        AuditPrompt("M12", "Identity chronicle warning", "Log warning when chronicle distillation fails.", "contains", "src/core/identity.py", "Chronicle distillation failed"),
        AuditPrompt("M13", "Identity archetype warning", "Log warning when archetype distillation fails.", "contains", "src/core/identity.py", "Archetype distillation failed"),
        AuditPrompt("M14", "Identity malformed JSON test", "Add regression test for malformed identity file.", "contains", "tests/core/test_identity.py", "test_identity_load_handles_malformed_json"),
        AuditPrompt("M15", "Identity reflect exception test", "Add regression test for LLM reflection exceptions.", "contains", "tests/core/test_identity.py", "test_reflect_handles_llm_exceptions"),
        AuditPrompt("M16", "Status callable typing", "Type _check callback for static safety.", "contains", "src/core/status.py", "Callable[[], bool]"),
        AuditPrompt("M17", "Status timeout handling", "Handle subprocess timeout cleanly in status self-test.", "contains", "src/core/status.py", "except subprocess.TimeoutExpired:"),
        AuditPrompt("M18", "Status stdout encoding guard", "Avoid None encoding attribute errors.", "contains", "src/core/status.py", "encoding = (sys.stdout.encoding or \"\").lower()"),
        AuditPrompt("M19", "Sleep latency telemetry", "Record reflection latency in ms and clamp non-finite values.", "contains", "src/core/sleep.py", "self._last_reflection_ms"),
        AuditPrompt("M20", "Sleep telemetry tests", "Add stats and note_activity tests for sleep daemon.", "contains", "tests/core/test_sleep.py", "test_note_activity_increments_turns"),
    ]


def _run_check(root: Path, prompt: AuditPrompt) -> AuditResult:
    path = root / prompt.target
    if prompt.check_kind == "file_exists":
        exists = path.exists()
        return AuditResult(prompt.id, prompt.title, exists, "exists" if exists else "missing")
    if prompt.check_kind == "contains":
        if not path.exists():
            return AuditResult(prompt.id, prompt.title, False, "missing file")
        needle = prompt.needle or ""
        text = path.read_text(encoding="utf-8")
        ok = needle in text
        return AuditResult(prompt.id, prompt.title, ok, "needle found" if ok else "needle missing")
    completed = subprocess.run(prompt.target, shell=True, check=False, cwd=root)
    ok = completed.returncode == 0
    return AuditResult(prompt.id, prompt.title, ok, f"exit_code={completed.returncode}")


def run_audit(*, report: Path | None = None) -> dict[str, object]:
    root = _repo_root()
    prompts = build_prompts()
    results = [_run_check(root, p) for p in prompts]
    passed = sum(1 for r in results if r.passed)
    payload: dict[str, object] = {
        "track": "model-audit-autopilot-20",
        "schema_version": "1",
        "total_prompts": len(prompts),
        "passed_prompts": passed,
        "failed_prompts": len(prompts) - passed,
        "all_passed": passed == len(prompts),
        "prompts": [asdict(p) for p in prompts],
        "results": [asdict(r) for r in results],
    }
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the 20-point model audit autopilot checks.")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("docs/collaboration/evidence/MODEL_AUDIT_AUTOPILOT_20_REPORT.json"),
    )
    args = parser.parse_args()
    payload = run_audit(report=args.report)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
