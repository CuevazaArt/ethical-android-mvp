"""
MER Block 10.5 — ADR 0018 presentation tier must not pull in ethical decision core.

Architecture: `prefetch_ack`, transparency S10, and basal-ganglia smoothing live beside
MalAbs / `KernelDecision`; they must not import AbsoluteEvil at module load.

Behavioral coverage: `tests/test_adr0018_presentation_tier.py`.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_PREFETCH_PATH = _REPO / "src" / "modules" / "prefetch_ack.py"


@pytest.mark.skipif(not _PREFETCH_PATH.is_file(), reason="prefetch_ack.py not in this branch yet")
def test_prefetch_ack_module_ast_has_no_absolute_evil_import():
    tree = ast.parse(_PREFETCH_PATH.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            m = node.module or ""
            names.add(m)
            for alias in node.names:
                names.add(f"{m}.{alias.name}" if m else alias.name)
    assert not any("absolute_evil" in n for n in names)


def test_transparency_s10_module_ast_has_no_absolute_evil_import():
    root = _REPO / "src" / "modules" / "transparency_s10.py"
    tree = ast.parse(root.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "absolute_evil" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "absolute_evil" not in alias.name


def test_basal_ganglia_module_ast_has_no_absolute_evil_import():
    mod = importlib.import_module("src.modules.basal_ganglia")
    assert mod is not None
    path = Path(mod.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "absolute_evil" not in node.module
