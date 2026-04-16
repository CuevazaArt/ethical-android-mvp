"""Smoke test for ``scripts/run_experiment_v5_sensitivity.py``."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_v5_main():
    path = ROOT / "scripts" / "run_experiment_v5_sensitivity.py"
    spec = importlib.util.spec_from_file_location("run_experiment_v5_sensitivity", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main


def test_v5_sensitivity_writes_artifacts(tmp_path: Path) -> None:
    main = _load_v5_main()
    out = tmp_path / "v5out"
    argv = [
        "run_experiment_v5_sensitivity.py",
        "--scenario-ids",
        "16",
        "--screening-denominator",
        "8",
        "--refinement-samples",
        "2",
        "--output-dir",
        str(out),
    ]
    old = sys.argv
    try:
        sys.argv = argv
        assert main() == 0
    finally:
        sys.argv = old

    assert (out / "screening_grid.csv").is_file()
    assert (out / "refinement_band.csv").is_file()
    assert (out / "boundaries.json").is_file()
    assert (out / "summary.json").is_file()
    assert (out / "full_kernel_note.json").is_file()
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["refinement_rows_written"] == 2
    assert summary["per_scenario"][0]["scenario_id"] == 16


def test_run_one_scenario_includes_boundary_distance() -> None:
    path = ROOT / "scripts" / "run_simplex_decision_map.py"
    spec = importlib.util.spec_from_file_location("run_simplex_decision_map", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    block = mod.run_one_scenario(16, denominator=12, bisect_edges=True)
    for r in block["grid_rows"]:
        if r.get("sampling_phase") == "screening":
            assert "distance_to_nearest_boundary" in r
            if block["bisections_along_edges"]:
                assert r["distance_to_nearest_boundary"] is not None
