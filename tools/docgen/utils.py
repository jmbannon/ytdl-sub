from typing import Dict

LEVEL_CHARS: Dict[int, str] = {0: "=", 1: "-", 2: "~", 3: "^"}


def section(name: str, level: int) -> str:
    return f"\n{name}\n{len(name) * LEVEL_CHARS[level]}\n"
