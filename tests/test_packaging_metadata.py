"""pyproject.toml core dependencies stay aligned with runtime imports."""

import tomllib
from pathlib import Path


def test_pyproject_lists_numpy_and_pydantic():
    root = Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    joined = " ".join(data["project"]["dependencies"])
    assert "numpy" in joined
    assert "pydantic" in joined
    assert data["project"]["requires-python"].startswith(">=")
