#!/usr/bin/env python3
"""
Swarm Governance Automation Script (V4.0 - Anonymous Pragmatism)
Automates the 'log' and 'commit' process for L2 Agents (Cursor, Copilot, Claude).
This replaces manual Markdown editing and corporate UIDs.

Usage:
    python scripts/swarm_sync.py --block W.1 --msg "Exported Nomadic Vision to Wiki"
"""

import argparse
import datetime
import subprocess
import sys
from pathlib import Path


def get_git_diff_files() -> list[str]:
    """Returns a list of tracked files that have been modified or added."""
    try:
        # Get unstaged changes
        unstaged = subprocess.check_output(
            ["git", "diff", "--name-only"], text=True
        ).splitlines()
        # Get staged changes
        staged = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], text=True
        ).splitlines()
        
        # Combine and remove duplicates
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


def update_changelog(block: str, msg: str, files: list[str], author: str = "Anonymous") -> Path:
    """Appends to the unified swarm_activity.md log."""
    log_dir = Path("docs/changelogs_l2")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "swarm_activity.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry_lines = [
        f"\n### 🛠️ Execution | Date: {timestamp} | Author: {author}",
        f"- **Block:** `{block}`",
        f"- **Message:** {msg}",
        "- **Files Modified:**"
    ]
    
    if not files:
        entry_lines.append("  - *(No files modified)*")
    else:
        for f in files:
            entry_lines.append(f"  - `{f}`")
            
    is_new = not log_file.exists()
    
    with open(log_file, "a", encoding="utf-8") as f:
        if is_new:
            f.write("# Anonymous Swarm Activity Log (V4.0)\n")
            f.write("This file is automatically managed by `scripts/swarm_sync.py`.\n")
        f.write("\n".join(entry_lines) + "\n")
        
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
    return True # Skip if script doesn't exist


def commit_changes(block: str, msg: str, author: str) -> bool:
    """Executes git add and git commit."""
    print("Staging all changes (git add -A)...")
    subprocess.run(["git", "add", "-A"], check=True)
    
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("Nothing to commit. Working tree clean.")
        return True
        
    commit_msg = f"[BLOCK: {block}] {msg}\n\nAuthor: {author}\nAuto-committed via swarm_sync.py (V4.0)"
    
    try:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during commit: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Swarm Synchronization Script (V4.0)")
    parser.add_argument("--block", required=True, help="Task Block from the Distribution Tree (e.g. W.1)")
    parser.add_argument("--msg", required=True, help="Brief summary of the atomic change")
    parser.add_argument("--author", default="Anonymous Agent", help="Optional LLM telemetry (e.g. 'Cursor', 'Copilot')")
    parser.add_argument("--no-verify", action="store_true", help="Skip invariant evaluation scripts")
    
    args = parser.parse_args()
    
    # 1. Identify territorial boundaries automatically
    changed_files = get_git_diff_files()
    untracked_files = get_untracked_files()
    all_target_files = sorted(list(set(changed_files + untracked_files)))
    
    has_meaningful_files = any(f for f in all_target_files if not f.startswith("docs/changelogs_l2"))
    if not has_meaningful_files:
        print("⚠️ No changes detected outside of L2 logs. Did you write any code yet?")
         
    # 2. Update unified log
    log_path = update_changelog(args.block, args.msg, all_target_files, args.author)
    print(f"[OK] Activity Log updated: {log_path}")
    
    # 3. Optional checks
    if not args.no_verify and not run_checks():
        print("[ERROR] L1 Audit Verification Failed! Aborting commit.")
        sys.exit(1)
        
    # 4. Git Execution
    if commit_changes(args.block, args.msg, args.author):
         print("\n[SUCCESS] SWARM ACTION COMPLETED SUCESSFULLY.")
         print("Pushing changes to remote to maintain Office A / Office B sync...")
         try:
             subprocess.run(["git", "push"], check=True)
             print("[OK] Changes pushed successfully.")
         except subprocess.CalledProcessError as e:
             print(f"\n[WARNING] Git push failed. You may need to pull/rebase first or push manually. Error: {e}")
    else:
         print("\n[FAILED] Git execution failed.")
         sys.exit(1)


if __name__ == "__main__":
    main()
