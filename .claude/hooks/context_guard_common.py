"""Shared helpers for Kyber Claude context guard hooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_SLICE_LINES = 200
MAX_ALLOWED_SLICE_LINES = 220
FULL_READ_LINE_ALLOWANCE = 220
FULL_READ_BYTE_ALLOWANCE = 24_000
MAX_LINE_SCAN_BYTES = 1_500_000


@dataclass(frozen=True, slots=True)
class FileAssessment:
    """Describe whether a file is safe to inline into Claude's context."""

    path: Path
    size_bytes: int
    line_count: int | None

    @property
    def is_large_inline(self) -> bool:
        """Return True when a whole-file inline would likely waste context."""
        if self.size_bytes > FULL_READ_BYTE_ALLOWANCE:
            return True
        return self.line_count is not None and self.line_count > FULL_READ_LINE_ALLOWANCE


def count_lines(path: Path) -> int | None:
    """Return the line count for manageable files, or None if skipped."""
    try:
        size_bytes = path.stat().st_size
    except OSError:
        return None

    if size_bytes > MAX_LINE_SCAN_BYTES:
        return None
    if size_bytes == 0:
        return 0

    line_breaks = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65_536), b""):
                line_breaks += chunk.count(b"\n")
    except OSError:
        return None
    return line_breaks + 1


def assess_file(path: Path) -> FileAssessment:
    """Return size and optional line-count metadata for a file."""
    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = 0
    return FileAssessment(path=path, size_bytes=size_bytes, line_count=count_lines(path))


def format_bytes(size_bytes: int) -> str:
    """Return a compact byte string for operator-facing messages."""
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.0f} KB"
    return f"{size_bytes} B"


def describe_file(assessment: FileAssessment) -> str:
    """Return a short description of the file size and, when known, line count."""
    parts = [format_bytes(assessment.size_bytes)]
    if assessment.line_count is not None:
        parts.insert(0, f"{assessment.line_count} lines")
    else:
        parts.insert(0, "line count unknown")
    return ", ".join(parts)