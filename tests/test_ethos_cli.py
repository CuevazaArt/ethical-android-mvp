"""Smoke tests for the emergency ``ethos`` CLI (``python -m src.ethos_cli``)."""

import io
import json
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_ethos_cli_diagnostics_json():
    from src.ethos_cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["diagnostics", "--json"])
    assert code == 0
    data = json.loads(buf.getvalue())
    assert "narrative_commitment_sha256" in data
    assert "integrity" in data


def test_ethos_cli_checkpoint_save_load_roundtrip(tmp_path):
    from src.ethos_cli import main

    p = tmp_path / "k.json"
    code = main(["checkpoint", "save", str(p)])
    assert code == 0
    assert p.is_file()
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["checkpoint", "load", str(p), "--json"])
    assert code == 0
    row = json.loads(buf.getvalue())
    assert row.get("loaded") is True


def test_ethos_cli_config_json_smoke():
    from src.ethos_cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["config", "--json"])
    assert code == 0
    data = json.loads(buf.getvalue())
    assert "experimental_risk" in data
    assert "by_family" in data
    assert "profile_alignment" in data


def test_ethos_cli_config_profiles_lists_runtime_names():
    from src.ethos_cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["config", "--profiles"])
    assert code == 0
    out = buf.getvalue()
    assert "baseline:" in out
    assert "judicial_demo:" in out
