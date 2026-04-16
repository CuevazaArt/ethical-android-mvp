"""pyproject.toml console_scripts entry points (ADR 0001, PROPOSAL_QUICK_WINS)."""

import tomllib
from pathlib import Path


def test_pyproject_declares_ethos_and_ethos_runtime_scripts():
    root = Path(__file__).resolve().parents[1]
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = data["project"]["scripts"]
    assert scripts.get("ethos") == "src.ethos_cli:main"
    assert scripts.get("ethos-runtime") == "src.chat_server:main"
