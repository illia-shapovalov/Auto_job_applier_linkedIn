from pathlib import Path

LOCK_FILE = Path("logs/bot-running.lock")


def acquire_instance_lock() -> None:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        handle = LOCK_FILE.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise RuntimeError(
            "Another bot instance appears to be running. "
            "Delete logs/bot-running.lock only after confirming "
            "no runAiBot.py process exists."
        ) from error

    handle.write("running\n")
    handle.close()


def release_instance_lock() -> None:
    LOCK_FILE.unlink(missing_ok=True)
