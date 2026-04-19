#!/usr/bin/env python3
"""
Swarm Governance Automation Script (V3.0)
Automates the 'claim', 'log', and 'commit' process for L2 Agents (Cursor, Copilot, Claude).
This replaces manual Markdown editing inside the IDE chat context, which leads to compliance failure.

Usage:
    python scripts/swarm_sync.py --uid COPILOT-BLUE-01 --block W.1 --msg "Exported Nomadic Vision to Wiki"
"""

import argparse
import datetime
import os
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


def update_changelog(uid: str, block: str, msg: str, files: list[str]) -> Path:
    """Creates or updates the markdown log in docs/changelogs_l2/."""
    log_dir = Path("docs/changelogs_l2")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{uid}.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    entry_lines = [
        f"\n### 🛡️ Swarm Action | Date: {timestamp}",
        f"- **UID:** `{uid}`",
        f"- **Block:** `{block}`",
        f"- **Message:** {msg}",
        "- **Territorial Claim (Files):**"
    ]
    
    if not files:
        entry_lines.append("  - *(No files modified)*")
    else:
        for f in files:
            entry_lines.append(f"  - `{f}`")
            
    is_new = not log_file.exists()
    
    with open(log_file, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"# Auto-Generated Swarm Log for {uid}\n")
            f.write("This file is managed by `scripts/swarm_sync.py`.\n")
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


def commit_changes(uid: str, block: str, msg: str, files_str: str) -> bool:
    """Executes git add and git commit with the Golden Commit formatting."""
    print("Staging all changes (git add -A)...")
    subprocess.run(["git", "add", "-A"], check=True)
    
    # Optional check: Did `add` actually stage anything?
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("Nothing to commit. Working tree clean.")
        return True
        
    commit_msg = f"[UID: {uid}] [BLOCK: {block}] [FILES: {files_str}]\n\n{msg}\n\nAuto-committed via swarm_sync.py"
    print(f"Committing with message header: [UID: {uid}] [BLOCK: {block}]")

    try:
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during commit: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Swarm Synchronization Script (L2 Agents)")
    parser.add_argument("--uid", required=True, help="Agent Designation (e.g. COPILOT-BLUE-01)")
    parser.add_argument("--block", required=True, help="Task Block from the Distribution Tree (e.g. W.1)")
    parser.add_argument("--msg", required=True, help="Brief summary of the atomic change")
    parser.add_argument("--no-verify", action="store_true", help="Skip invariant evaluation scripts")
    
    args = parser.parse_args()
    
    # 1. Identify territorial boundaries automatically
    changed_files = get_git_diff_files()
    untracked_files = get_untracked_files()
    all_target_files = sorted(list(set(changed_files + untracked_files)))
    
    has_meaningful_files = any(f for f in all_target_files if not f.startswith("docs/changelogs_l2"))
    if not has_meaningful_files:
        print("⚠️ No changes detected outside of L2 logs. Did you write any code yet?")
        # We don't abort, they might just be initializing their log
        
    # Summarize files for commit
    meaningful = [f for f in all_target_files if not f.startswith("docs/changelogs_l2")]
    if len(meaningful) > 3:
        files_str = f"{', '.join(meaningful[:3])} and {len(meaningful)-3} more"
    elif meaningful:
         files_str = ", ".join(meaningful)
    else:
         files_str = "None"
         
    # 2. Update local log
    log_path = update_changelog(args.uid, args.block, args.msg, all_target_files)
    print(f"✅ Identity Log updated: {log_path}")
    
    # 3. Optional checks
    if not args.no_verify and not run_checks():
        print("❌ L1 Audit Verification Failed! Aborting commit.")
        print("Please fix the validation errors and run swarm_sync.py again.")
        sys.exit(1)
        
    # 4. Git Execution
    if commit_changes(args.uid, args.block, args.msg, files_str):
         print("\n🚀 SWARM ACTION COMPLETED SUCESSFULLY.")
         print("Ready to push. You can now execute `git push` on your branch.")
    else:
         print("\n❌ Git execution failed.")
         sys.exit(1)


if __name__ == "__main__":
    main()
