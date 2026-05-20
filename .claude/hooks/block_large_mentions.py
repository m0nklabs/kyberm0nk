#!/usr/bin/env python3
"""Block prompt-time @file inlines for large files that would waste context."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from context_guard_common import (  # pylint: disable=import-error
    DEFAULT_SLICE_LINES,
    assess_file,
    describe_file,
)

MENTION_PATTERN = re.compile(r"(?<!\S)@(?P<path>[^\s,;:(){}\[\]<>]+)")


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


def resolve_candidate(candidate: str, cwd: Path) -> Path | None:
    """Resolve a prompt @mention into a local filesystem path when possible."""
    if ":" in candidate and not candidate.startswith(("/", "./", "../", "~/")):
        return None
    if candidate.startswith("~/"):
        return Path(candidate).expanduser().resolve()
    if candidate.startswith("/"):
        return Path(candidate).resolve()
    return (cwd / candidate).resolve()


def build_reason(entries: list[str]) -> str:
    """Build the user-visible block reason for large @file inlines."""
    joined = "; ".join(entries)
    return (
        "Blocked large @file inline that would dump too much context at once: "
        f"{joined}. Use Grep or Glob first, then Read those files in slices of about "
        f"{DEFAULT_SLICE_LINES} lines instead of inlining them with @file."
    )


def block(reason: str) -> int:
    """Emit a structured block response for the UserPromptSubmit hook."""
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": reason,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "Kyber blocks large @file inlines to protect context quality. "
                        "Use targeted search plus sliced Read calls when a file is large."
                    ),
                },
            }
        )
    )
    return 0


def main() -> int:
    """Reject prompts that try to inline large local files with @mentions."""
    payload = load_input()
    prompt = payload.get("prompt")
    cwd_value = payload.get("cwd")
    if not isinstance(prompt, str) or not isinstance(cwd_value, str):
        return 0

    cwd = Path(cwd_value)
    blocked_entries: list[str] = []

    for match in MENTION_PATTERN.finditer(prompt):
        candidate = match.group("path")
        resolved = resolve_candidate(candidate, cwd)
        if resolved is None or not resolved.exists() or not resolved.is_file():
            continue

        assessment = assess_file(resolved)
        if assessment.is_large_inline:
            blocked_entries.append(f"{resolved} ({describe_file(assessment)})")

    if not blocked_entries:
        return 0
    return block(build_reason(blocked_entries[:3]))


if __name__ == "__main__":
    raise SystemExit(main())