#!/usr/bin/env python3
"""
Continuous Collaboration Audit
Enforces L1 Supremacy Governance Rules (MERGE-PREVENT-01 & L1-SUPREMACY-01).

Level 2 teams (Claude, Cursor, VisualStudio) MUST run and pass this script
before their branches can be accepted into the integration funnel.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Path segments to skip when scanning for merge markers (nested deps / vendored trees / worktrees).
_MERGE_MARKER_SKIP_PARTS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "dist",
        "build",
        "htmlcov",
        ".ruff_cache",
        "site-packages",
    }
)


def _skip_path_for_merge_scan(path: Path) -> bool:
    for part in path.parts:
        if part in _MERGE_MARKER_SKIP_PARTS:
            return True
        if part.startswith("ethical-android-mvp-feature-"):
            return True
    return False


_MERGE_SCAN_SUFFIXES: tuple[str, ...] = (
    ".py",
    ".md",
    ".mdc",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
)


def _path_matches_merge_scan_suffix(path: Path) -> bool:
    n = path.name.lower()
    return any(n.endswith(s) for s in _MERGE_SCAN_SUFFIXES)


def _tracked_files_for_merge_scan(root: Path) -> list[Path] | None:
    """Return tracked text-ish files via ``git ls-files`` (fast; ignores vendor trees)."""
    try:
        r = subprocess.run(
            ["git", "ls-files", "-z", "--", "."],
            cwd=root,
            capture_output=True,
            check=False,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        out: list[Path] = []
        for rel in r.stdout.split(b"\0"):
            if not rel:
                continue
            p = root / rel.decode("utf-8", errors="replace")
            if _path_matches_merge_scan_suffix(p):
                out.append(p)
        return out
    except Exception:
        return None


def _rglob_fallback_merge_files(root: Path) -> list[Path]:
    """Fallback when ``git ls-files`` is unavailable — scan project roots only (no whole-disk ``rglob``)."""
    out: list[Path] = []
    patterns = ("*.py", "*.md", "*.mdc", "*.yml", "*.yaml", "*.json", "*.txt")
    for pattern in patterns:
        for file_path in root.glob(pattern):
            if file_path.is_file():
                out.append(file_path)
    for sub in ("src", "tests", "docs", "scripts", ".cursor"):
        base = root / sub
        if not base.is_dir():
            continue
        for pattern in patterns:
            for file_path in base.rglob(pattern):
                if not file_path.is_file():
                    continue
                if _skip_path_for_merge_scan(file_path):
                    continue
                out.append(file_path)
    # De-dupe stable order
    seen: set[str] = set()
    unique: list[Path] = []
    for p in out:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def git_diff_files() -> list[str]:
    """Returns a list of files modified in the current branch relative to origin/main."""
    try:
        # Get files changed between the current working tree/branch and origin/main
        # If origin/main isn't fetched, it might fail. Fallback to just HEAD diff.
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True, text=True, check=False
            )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except Exception:
        return []


def check_no_merge_markers(directory: Path) -> list[str]:
    """Scans for leftover git merge markers which indicate unresolved 'Merge Hell'."""
    violations = []
    marker_pattern = re.compile(r'^(<<<<<<<|=======|>>>>>>>)( |$)')

    candidates = _tracked_files_for_merge_scan(directory)
    if candidates is None:
        candidates = _rglob_fallback_merge_files(directory)

    for file_path in candidates:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if marker_pattern.match(line):
                        violations.append(
                            f"{file_path}:{line_num} contains unresolved git merge marker."
                        )
        except Exception:
            pass
    return violations


def check_changelog_namespace(changelog_path: Path) -> list[str]:
    """
    Enforces MERGE-PREVENT-01: CHANGELOG Namespace Segregation.
    Ensures that under Month headers (##), entries are categorized by Team subheaders (###).
    """
    violations = []
    if not changelog_path.exists():
        return ["CHANGELOG.md not found."]

    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple heuristic: If there are ## Month headers, the immediate next content
    # shouldn't be a direct bullet list of features without a ### Team header first.
    # We look for a pattern where `## ` is followed immediately by `- ` ignoring empty lines.
    
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)[1:]
    # Only enforce the new namespace isolation for the top 2 sections
    for i, section in enumerate(sections[:2]):
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        if not lines:
            continue
            
        header_text = lines[0]
        # Ignore legacy sections (e.g., 2024 or older stuff)
        if "2024" in header_text or "2025" in header_text:
            continue

        # Check the first operational content line
        for line in lines[1:]:
            if line.startswith('###'):
                break # Valid: Team namespace found.
            if line.startswith('- ') or line.startswith('* '):
                if not "Historical" in header_text:
                    violations.append(
                        f"CHANGELOG.md format violation under '## {header_text}': "
                        f"Found bullet point '{line[:30]}...' without a preceding '### Team' subheader. "
                        f"(MERGE-PREVENT-01 Rule 2 Namespace Isolation)"
                    )
                break
    return violations


def check_protected_files(modified_files: list[str]) -> list[str]:
    """
    Enforces L1-SUPREMACY-01: Protects AGENTS.md and .cursor/rules/
    """
    violations = []
    for file in modified_files:
        if file == 'AGENTS.md' or file.startswith('.cursor/rules/'):
            # This is an advisory rule. A human (Juan/Antigravity) will ultimately review it.
            violations.append(
                f"[L1-SUPREMACY-01] WARNING: You have modified the protected governance file '{file}'. "
                f"As an L2 executing unit, you MUST have explicit authorization from Juan (L0) or "
                f"Antigravity (L1) for this change to be accepted into the integration funnel."
            )
    return violations


def main():
    import sys
    # Ensure Windows console doesn't crash on unicode
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    def safe_print(msg):
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'replace').decode('ascii'))

    safe_print("="*60)
    safe_print(" ETHOS KERNEL - CONTINUOUS COLLABORATION AUDIT")
    safe_print("="*60)
    
    root_dir = Path(__file__).parent.parent.parent
    violations = []

    safe_print("[*] Checking for unresolved merge markers...")
    marker_violations = check_no_merge_markers(root_dir)
    violations.extend(marker_violations)

    safe_print("[*] Checking CHANGELOG.md namespace compliance...")
    changelog_path = root_dir / "CHANGELOG.md"
    
    # Check changelog violations
    raw_cl_violations = check_changelog_namespace(changelog_path)
    violations.extend(raw_cl_violations)

    safe_print("[*] Checking for modifications to protected L1 governance files...")
    modified_files = git_diff_files()
    violations.extend(check_protected_files(modified_files))

    if violations:
        safe_print("\n[!] AUDIT FAILED: The following invariants were violated:\n")
        has_fatal = False
        for v in violations:
            if v.startswith("[L1-SUPREMACY-01] WARNING:"):
                safe_print(f"  [WARN] {v}")
            else:
                safe_print(f"  [FAIL] {v}")
                has_fatal = True
        
        if has_fatal:
            safe_print("\n[!] L2 Agents: You must resolve the fatal errors above before merging.")
            sys.exit(1)
        else:
            safe_print("\n[OK] Audit passed with L1 Governance warnings. Subject to human review.")
            sys.exit(0)
    else:
        safe_print("\n[OK] AUDIT PASSED: All collaboration invariants satisfied.")
        sys.exit(0)

if __name__ == '__main__':
    main()
