"""
Thread-safe database concurrency utilities.
Provides singleton locks per SQLite file to prevent 'database is locked' operational errors 
when utilizing asyncio workers/threads in the Ethos Kernel.
"""

from __future__ import annotations

import contextlib
import sqlite3
import threading
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

# Process-level static locks per file path
_DB_LOCKS: dict[str, threading.Lock] = defaultdict(threading.Lock)

def get_db_lock(db_path: Path | str) -> threading.Lock:
    """Returns the process-wide thread lock for the given SQLite database path."""
    return _DB_LOCKS[str(db_path)]


@contextlib.contextmanager
def sqlite_safe_write(
    db_path: Path | str, 
    timeout_s: float = 30.0
) -> Iterator[sqlite3.Connection]:
    """
    Context manager providing a safe SQLite connection for writing.
    It blocks on a thread-lock first to serialize concurrent Python threads efficiently, 
    and then sets `BEGIN IMMEDIATE` to prevent SQLite deferred-lock deadlocks internally.
    """
    path_str = str(db_path)
    
    # Bypass thread locks for strictly in-memory databases since they are connection bounded anyway
    is_memory = path_str == ":memory:"
    
    if not is_memory:
        # Guarantee cross-thread serialization locally within this instance
        lock = _DB_LOCKS[path_str]
        lock.acquire()
    
    try:
        # Create connection with increased timeout for resilience
        conn = sqlite3.connect(path_str, timeout=timeout_s, isolation_level="IMMEDIATE")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL") # Enable Write-Ahead Logging for better concurrency
        try:
            yield conn
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()
    finally:
        if not is_memory:
            lock.release()

