#!/usr/bin/env python3
"""
X Archive - git_sync.py

Git synchronization script for X Archive.
Handles git add, commit, and push operations after archive pipeline completes.
Uses a separate git lock to avoid conflicts with other git operations.
"""

import subprocess
import sys
import contextlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
GIT_DIR = ROOT / ".git"
GIT_LOCK_FILE = ROOT / ".locks" / "git.lock"

def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] {message}", flush=True)

def log_error(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] ERROR: {message}", file=sys.stderr, flush=True)

def run_git(args: list[str], check=True) -> subprocess.CompletedProcess:
    """Run a git command in the repository root."""
    cmd = ["git", "-C", str(ROOT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result

@contextlib.contextmanager
def acquire_git_lock():
    """Acquire git lock using fcntl."""
    import fcntl
    GIT_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with GIT_LOCK_FILE.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f"Another git operation is already running. Lock: {GIT_LOCK_FILE}")
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

def has_changes() -> bool:
    """Check if there are any staged or unstaged changes."""
    result = run_git(["status", "--porcelain"], check=False)
    return bool(result.stdout.strip())

def get_status_summary() -> str:
    """Get a summary of changes for commit message."""
    result = run_git(["status", "--porcelain"], check=False)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    
    stats = {"added": 0, "modified": 0, "deleted": 0, "untracked": 0}
    for line in lines:
        status = line[:2]
        if status == "??":
            stats["untracked"] += 1
        elif status[0] == "A":
            stats["added"] += 1
        elif status[0] == "M":
            stats["modified"] += 1
        elif status[0] == "D":
            stats["deleted"] += 1
        elif status[1] == "M":
            stats["modified"] += 1
        elif status[1] == "D":
            stats["deleted"] += 1
    
    parts = []
    if stats["added"]:
        parts.append(f"{stats['added']} added")
    if stats["modified"]:
        parts.append(f"{stats['modified']} modified")
    if stats["deleted"]:
        parts.append(f"{stats['deleted']} deleted")
    if stats["untracked"]:
        parts.append(f"{stats['untracked']} untracked")
    
    return ", ".join(parts) if parts else "no changes"

def main() -> int:
    if not GIT_DIR.exists():
        log_error(f"Not a Git repository: {ROOT}")
        return 1
    
    try:
        # Acquire git lock
        with acquire_git_lock():
            log("Git lock acquired.")
            
            # Check for changes
            if not has_changes():
                log("No changes to commit.")
                return 0
            
            # Show status
            status_summary = get_status_summary()
            log(f"Changes detected: {status_summary}")
            
            # Add all changes in allowed directories
            allowed_dirs = ["data/", "archive/", "assets/"]
            for d in allowed_dirs:
                run_git(["add", d])
            
            # Check if anything was staged
            result = run_git(["diff", "--cached", "--name-only"], check=False)
            if not result.stdout.strip():
                log("No changes in allowed directories to commit.")
                return 0
            
            # Create commit message
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            commit_msg = f"Archive sync: {status_summary} ({timestamp})"
            
            # Commit
            run_git(["commit", "-m", commit_msg])
            log(f"Committed: {commit_msg}")
            
            # Push
            run_git(["push", "origin", "main"])
            log("Pushed to origin/main")
            
            return 0
            
    except RuntimeError as e:
        log_error(str(e))
        return 1
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())