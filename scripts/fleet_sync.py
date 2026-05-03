#!/usr/bin/env python3
"""
Fleet Synchronization Script (V2.159)

Replaces the deprecated fleet synchronization script (fleet_sync superseded older tooling, retired V2.159).
Automates the 'log' and 'commit' process for kernel instances.

Usage:
    python scripts/fleet_sync.py --cycle v2.159 --msg "Charter completeness sprint"
"""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path


def get_git_diff_files() -> list[str]:
    """Returns a list of tracked files that have been modified or added."""
    try:
        unstaged = subprocess.check_output(
            ["git", "diff", "--name-only"], text=True
        ).splitlines()
        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], text=True
        ).splitlines()
        all_changed = sorted(list(set(unstaged + staged)))
        return [f.strip() for f in all_changed if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_untracked_files() -> list[str]:
    """Returns a list of untracked files."""
    try:
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], text=True
        ).splitlines()
        return [f.strip() for f in untracked if f.strip()]
    except subprocess.CalledProcessError:
        return []


def update_changelog(
    cycle: str, msg: str, files: list[str], author: str = "Anonymous"
) -> Path:
    """Appends to the fleet activity log."""
    log_dir = Path("docs/changelogs_l2")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "fleet_activity.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry_lines = [
        f"\n### Execution | Date: {timestamp} | Author: {author}",
        f"- **Cycle:** `{cycle}`",
        f"- **Message:** {msg}",
        "- **Files Modified:**",
    ]

    if not files:
        entry_lines.append("  - *(No files modified)*")
    else:
        for f in files:
            entry_lines.append(f"  - `{f}`")

    is_new = not log_file.exists()

    with open(log_file, "a", encoding="utf-8") as fh:
        if is_new:
            fh.write("# Fleet Activity Log (V2.159+)\n")
            fh.write("Automatically managed by `scripts/fleet_sync.py`.\n")
        fh.write("\n".join(entry_lines) + "\n")

    return log_file


def run_checks() -> bool:
    """Runs the collaborative invariants check."""
    check_script = Path("scripts/eval/verify_collaboration_invariants.py")
    if check_script.exists():
        print(f"Running compliance check: {check_script}...")
        try:
            subprocess.check_call([sys.executable, str(check_script)])
            return True
        except subprocess.CalledProcessError:
            return False
    return True


def commit_changes(cycle: str, msg: str, author: str) -> bool:
    """Executes git add and git commit."""
    print("Staging all changes (git add -A)...")
    subprocess.run(["git", "add", "-A"], check=True)

    status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if not status.stdout.strip():
        print("Nothing to commit. Working tree clean.")
        return True

    commit_msg = (
        f"[{cycle}] {msg}\n\n"
        f"Author: {author}\n"
        f"Auto-committed via fleet_sync.py (V2.159)"
    )

    try:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during commit: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Fleet Synchronization Script (V2.159)")
    parser.add_argument(
        "--cycle", required=True, help="Release cycle identifier (e.g. v2.159)"
    )
    parser.add_argument("--msg", required=True, help="Brief summary of the change")
    parser.add_argument(
        "--author",
        default="Anonymous",
        help="Optional instance identifier (e.g. 'Copilot', 'Claude')",
    )
    parser.add_argument(
        "--no-verify", action="store_true", help="Skip invariant evaluation scripts"
    )

    args = parser.parse_args()

    changed_files = get_git_diff_files()
    untracked_files = get_untracked_files()
    all_target_files = sorted(list(set(changed_files + untracked_files)))

    has_meaningful_files = any(
        f
        for f in all_target_files
        if not f.startswith("docs/changelogs_l2")
    )
    if not has_meaningful_files:
        print(
            "[WARN] No code changes outside docs/changelogs_l2. "
            "Did you write any code yet?"
        )

    log_path = update_changelog(args.cycle, args.msg, all_target_files, args.author)
    print(f"[OK] Activity Log updated: {log_path}")

    if not args.no_verify and not run_checks():
        print("[ERROR] Invariant verification failed. Aborting commit.")
        sys.exit(1)

    if commit_changes(args.cycle, args.msg, args.author):
        print("\n[OK] FLEET SYNC COMPLETED SUCCESSFULLY.")
        print("Pushing changes to remote...")
        try:
            subprocess.run(["git", "push"], check=True)
            print("[OK] Changes pushed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"\n[WARNING] Git push failed. Push manually. Error: {e}")
    else:
        print("\n[FAILED] Git commit failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
