"""Validate and emit the fixed bounty entry using only the standard library."""

import os
from pathlib import Path


ENTRY_LINE = "I can't make it. I'm already booked as the root cause in another meeting."
FORBIDDEN_LINE_BREAKS = frozenset("\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029")


def validated_utf8(text: str) -> bytes:
    """Return exact UTF-8 bytes only for a non-blank, 1–200-character line."""
    if not 1 <= len(text) <= 200:
        raise ValueError("Entry length must be between 1 and 200 characters.")
    if not text.strip():
        raise ValueError("Entry must not be blank.")
    if FORBIDDEN_LINE_BREAKS.intersection(text):
        raise ValueError("Entry must not contain any line separator.")
    return text.encode("utf-8")


def main() -> None:
    payload = validated_utf8(ENTRY_LINE)
    destination = Path(os.environ.get("OUTPUT_DIR", "/output")) / "entry.txt"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)


if __name__ == "__main__":
    main()
