"""pyproject.toml core dependencies stay aligned with runtime imports."""

import tomllib
from pathlib import Path


def test_pyproject_lists_numpy_and_pydantic():
    root = Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    proj = data["project"]
    joined = " ".join(proj["dependencies"])
    assert "numpy" in joined
    assert "pydantic" in joined
    assert proj["requires-python"].startswith(">=")
    assert proj["version"] == "0.0.0"
    assert "keywords" in proj
    extras = proj["optional-dependencies"]
    assert "runtime" in extras and "dev" in extras
    assert extras["theater"] == []
