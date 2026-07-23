from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "runAiBot.py"


def replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)
    if count == 0:
        if new in text:
            print(f"Already applied: {description}")
            return text
        raise RuntimeError(f"Could not find patch target: {description