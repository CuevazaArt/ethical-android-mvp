"""PrecedentRAG persistence (D2) — I/O and logging contract."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.precedent_rag import PrecedentRAG


def test_precedent_rag_save_load_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "precedents.json"
    r1 = PrecedentRAG(str(p))
    r1.add_precedent("lost wallet", "returned", 0.9, "civic good", ["trust"])
    r2 = PrecedentRAG(str(p))
    assert len(r2.index) == 1
    assert r2.index[0].scenario_summary == "lost wallet"
    assert "trust" in r2.index[0].trauma_tags


def test_precedent_rag_save_makedirs_failure_logs_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    p = tmp_path / "a" / "b.json"
    r = PrecedentRAG(str(p))
    caplog.set_level(logging.WARNING)

    def _boom(*_a, **_k):
        raise OSError(13, "Permission denied")

    monkeypatch.setattr("src.modules.precedent_rag.os.makedirs", _boom)
    r._save()
    assert "failed to persist" in caplog.text
    assert str(p) in caplog.text
