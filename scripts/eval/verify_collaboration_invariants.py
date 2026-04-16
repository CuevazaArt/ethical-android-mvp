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

    for ext in ['.py', '.md', '.mdc', '.yml', '.yaml', '.json', '.txt']:
        for file_path in directory.rglob(f"*{ext}"):
            if '.venv' in str(file_path) or '.git' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if marker_pattern.match(line):
                            violations.append(f"{file_path}:{line_num} contains unresolved git merge marker.")
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
