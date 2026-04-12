"""Smoke tests for empirical pilot fixture + runner (Issue 3)."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"
SCRIPT = ROOT / "scripts" / "run_empirical_pilot.py"


def _load_run_pilot():
    spec = importlib.util.spec_from_file_location("run_empirical_pilot", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.run_pilot


def test_fixture_schema():
    with open(FIXTURE, encoding="utf-8") as f:
        data = json.load(f)
    assert data["version"] == 1
    rs = data.get("reference_standard") or {}
    assert rs.get("tier") == "internal_pilot"
    assert "scenarios" in data
    for s in data["scenarios"]:
        assert isinstance(s["id"], int)
        assert 1 <= s["id"] <= 9
        assert "reference_action" in s


def test_run_pilot_importable():
    run_pilot = _load_run_pilot()
    rows, summary, _ref = run_pilot(FIXTURE)
    assert len(rows) == summary["scenarios"]
    assert summary["with_reference"] == len(rows)
    for r in rows:
        assert r["kernel"]
        assert r["baseline_first"]
        assert r["baseline_max_impact"]


def test_run_pilot_script_exit_zero():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_empirical_pilot.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert "summary" in out and "rows" in out
    assert "reference_standard" in out


def test_run_pilot_script_writes_output_file(tmp_path):
    out_path = tmp_path / "pilot_out.json"
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_empirical_pilot.py"),
            "--output",
            str(out_path),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert "rows" in data and "summary" in data and "meta" in data
    assert data["meta"]["kernel"]["seed"] == 42
    assert "reference_standard" in data["meta"]
    assert data["summary"]["scenarios"] == 9
