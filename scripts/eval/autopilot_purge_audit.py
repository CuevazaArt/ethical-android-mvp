"""
Autopilot Purge Audit — L1-AUDIT-PULSE
Detecta:
  1. Módulos no importados en ningún otro archivo del proyecto
  2. Módulos funcionalmente similares (nombres de clase/función solapados)
  3. Módulos stub/mock que ya fueron reemplazados

Salida: reporte de candidatos a purga con justificación.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC  = ROOT / "src"

# ── helpers ──────────────────────────────────────────────────────────────────

def all_py(base: Path) -> list[Path]:
    return [
        p for p in base.rglob("*.py")
        if "__pycache__" not in str(p) and ".venv" not in str(p)
    ]

def module_key(path: Path) -> str:
    """Return dotted import key relative to src."""
    try:
        rel = path.relative_to(SRC)
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)
    except ValueError:
        return str(path.stem)

def read_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def extract_top_names(p: Path) -> set[str]:
    """Return all top-level class and function names defined in a file."""
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names

# ── 1. Build import index ─────────────────────────────────────────────────────

all_files = all_py(SRC)
stem_to_path: dict[str, Path] = {}
for f in all_files:
    stem_to_path[f.stem] = f

# Aggregate all text across the repo (including tests & scripts)
all_project_text = ""
for f in all_py(ROOT):
    all_project_text += read_safe(f)

# ── 2. Unused module scan ─────────────────────────────────────────────────────

SKIP_STEMS = {"__init__", "conftest", "app", "kernel", "main"}
SKIP_DIRS  = {"sandbox", "experimental"}

unused: list[Path] = []
for stem, path in sorted(stem_to_path.items()):
    if stem in SKIP_STEMS:
        continue
    if any(d in str(path) for d in SKIP_DIRS):
        continue
    # Count references to this module by stem name (import foo / from ...foo)
    pattern = rf'\b{re.escape(stem)}\b'
    matches = re.findall(pattern, all_project_text)
    # A file referencing itself counts as 1; also its own definition lines
    # Threshold: ≤ 3 hits means it's almost certainly unused
    if len(matches) <= 3:
        unused.append(path)

# ── 3. Functional duplicate scan ─────────────────────────────────────────────
# Group files by their exported top-level names — large overlap = functional dup

name_to_files: dict[str, list[Path]] = defaultdict(list)
for f in all_files:
    for name in extract_top_names(f):
        if len(name) >= 6 and name != "__init__":  # skip tiny helpers and constructors
            name_to_files[name].append(f)

functional_dups: dict[str, list[Path]] = {
    name: paths for name, paths in name_to_files.items()
    if len(paths) >= 2
}

# ── 4. Mock/stub pattern scan ─────────────────────────────────────────────────

MOCK_PATTERNS = ["mock", "stub", "fake", "dummy", "placeholder", "legacy"]
mock_files: list[Path] = []
for f in all_files:
    name_lower = f.stem.lower()
    if any(p in name_lower for p in MOCK_PATTERNS):
        content = read_safe(f)
        # Only flag if they're not referenced well
        if all_project_text.count(f.stem) <= 4:
            mock_files.append(f)

# ── 5. Report ─────────────────────────────────────────────────────────────────

print("=" * 70)
print("  AUTOPILOT PURGE AUDIT — L1 PILOT SCAN")
print("=" * 70)

print(f"\n[1] UNUSED MODULES ({len(unused)} candidates):")
for p in unused:
    rel = p.relative_to(ROOT)
    print(f"    DEL  {rel}")

print(f"\n[2] FUNCTIONAL DUPLICATES (same class/function in multiple files):")
shown = 0
for name, paths in sorted(functional_dups.items(), key=lambda x: -len(x[1])):
    if shown >= 30:
        break
    rels = [str(p.relative_to(ROOT)) for p in paths]
    print(f"    '{name}' defined in {len(paths)} files:")
    for r in rels:
        print(f"      → {r}")
    shown += 1

print(f"\n[3] MOCK/STUB FILES ({len(mock_files)} candidates):")
for p in mock_files:
    print(f"    STUB  {p.relative_to(ROOT)}")

print("\n" + "=" * 70)
print(f"  SUMMARY: {len(unused)} unused | {len(functional_dups)} dup symbols | {len(mock_files)} stubs")
print("=" * 70)
