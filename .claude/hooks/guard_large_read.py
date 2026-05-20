#!/usr/bin/env python3
"""Block oversized Read tool calls and force explicit slicing."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from context_guard_common import (  # pylint: disable=import-error
    DEFAULT_SLICE_LINES,
    MAX_ALLOWED_SLICE_LINES,
    assess_file,
    describe_file,
)


def load_input() -> dict[str, Any]:
    """Return the hook payload from stdin."""
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        return {}
    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def parse_positive_int(value: Any, default: int) -> int:
    """Convert a JSON scalar to a positive integer fallback."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def build_reason(path: Path, description: str, offset: int) -> str:
    """Build the deny message shown to Claude when the read is too broad."""
    return (
        f"Blocked oversized Read for {path} ({description}). "
        f"Use Grep or Glob to narrow the target first, then read explicit slices of "
        f"no more than {DEFAULT_SLICE_LINES} lines. Suggested next step: Read "
        f"file_path={path} offset={offset} limit={DEFAULT_SLICE_LINES}. "
        "Do not request a whole-file read or another unbounded slice for this file."
    )


def deny(reason: str) -> int:
    """Emit a structured deny response for the PreToolUse hook."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def main() -> int:
    """Apply Kyber's large-read slicing policy."""
    payload = load_input()
    if payload.get("tool_name") != "Read":
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return 0

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return 0

    assessment = assess_file(path)
    if not assessment.is_large_inline:
        return 0

    limit = parse_positive_int(tool_input.get("limit"), default=0)
    if 0 < limit <= MAX_ALLOWED_SLICE_LINES:
        return 0

    offset = parse_positive_int(tool_input.get("offset"), default=1)
    return deny(build_reason(path, describe_file(assessment), offset))


if __name__ == "__main__":
    raise SystemExit(main())