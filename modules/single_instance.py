from __future__ import annotations

import os
from pathlib import Path


LOCK_FILE = Path("logs/bot-running.lock")


def _pid_is_running(pid: int) -> bool:
    """Return True when a process with *pid* is still alive."""
    if pid <= 0:
        return False

    if os.name == "nt":
        try:
            import ctypes

            process_query_limited_information = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                process_query_limited_information,
                False,
                pid,
            )

            if not handle:
                return False

            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        except Exception:
            return False

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    else:
        return True


def acquire_instance_lock() -> None:
    """Acquire a PID lock, removing it only when it is demonstrably stale."""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    if LOCK_FILE.exists():
        try:
            existing_pid = int(
                LOCK_FILE.read_text(encoding="utf-8").strip()
            )
        except (OSError, ValueError):
            existing_pid = -1

        if _pid_is_running(existing_pid):
            raise RuntimeError(
                "Another bot instance is already running "
                f"with process ID {existing_pid}."
            )

        LOCK_FILE.unlink(missing_ok=True)

    try:
        handle = LOCK_FILE.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise RuntimeError(
            "Another bot instance acquired the lock at the same time."
        ) from error

    handle.write(f"{os.getpid()}\n")
    handle.close()


def release_instance_lock() -> None:
    """Release this process's lock without deleting another process's lock."""
    if not LOCK_FILE.exists():
        return

    try:
        owner_pid = int(
            LOCK_FILE.read_text(encoding="utf-8").strip()
        )
    except (OSError, ValueError):
        owner_pid = -1

    if owner_pid in {-1, os.getpid()}:
        LOCK_FILE.unlink(missing_ok=True)
