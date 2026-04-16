"""Cross-process advisory lock for checkpoint files (fcntl / msvcrt)."""

from __future__ import annotations

import contextlib
import sys
import time
from collections.abc import Iterator
from pathlib import Path


@contextlib.contextmanager
def advisory_file_lock(
    lock_path: Path,
    *,
    poll_s: float = 0.05,
    timeout_s: float = 60.0,
) -> Iterator[None]:
    """
    Exclusive lock on ``lock_path`` (created if missing).

    On POSIX uses ``flock``; on Windows uses ``msvcrt.locking`` with a spin loop.
    Raises TimeoutError if ``timeout_s`` elapses without acquiring the lock.
    """
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_s

    if sys.platform == "win32":
        import msvcrt

        with open(lock_path, "wb+") as fh:
            fh.write(b"\0")
            fh.flush()
            while True:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"Could not acquire file lock: {lock_path}") from None
                    time.sleep(poll_s)
            try:
                yield
            finally:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
    else:
        import fcntl

        with open(lock_path, "a+", encoding="utf-8") as fh:
            while True:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f"Could not acquire file lock: {lock_path}") from None
                    time.sleep(poll_s)
            try:
                yield
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
