#!/usr/bin/env python3
"""Render a low-noise Claude Code status line for context pressure."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

BAR_WIDTH = 10
CONTEXT_MISMATCH_TOLERANCE = 4_096
GUARDIAN_TIMEOUT_SECONDS = 0.2
DEFAULT_AUTO_COMPACT_PCT = 95
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_RESET = "\033[0m"


def load_payload() -> dict[str, Any]:
    """Return the JSON payload piped in by Claude Code."""
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        return {}
    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def as_int(value: Any) -> int:
    """Convert a JSON scalar into an integer with a zero fallback."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def maybe_fetch_guardian_context(model_name: str, prefer_runtime: bool = False) -> int:
    """Return Guardian context metadata for the active model."""
    base_url = (os.environ.get("ANTHROPIC_BASE_URL") or "").strip().rstrip("/")
    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()

    if not model_name or not base_url or not api_key:
        return 0
    if not (
        base_url.startswith("http://127.0.0.1:11434")
        or base_url.startswith("http://localhost:11434")
    ):
        return 0

    models_url = f"{base_url}/models" if base_url.endswith("/v1") else f"{base_url}/v1/models"
    request = urllib.request.Request(models_url, headers={"x-api-key": api_key})

    try:
        with urllib.request.urlopen(request, timeout=GUARDIAN_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except (OSError, TimeoutError, ValueError, json.JSONDecodeError, urllib.error.URLError):
        return 0

    for item in payload.get("data", []):
        if item.get("id") != model_name:
            continue
        field_order = ("context", "advertised_context", "max_context") if prefer_runtime else (
            "advertised_context",
            "max_context",
            "context",
        )
        for field_name in field_order:
            context_window_size = as_int(item.get(field_name))
            if context_window_size > 0:
                return context_window_size
        return 0
    return 0


def choose_context_window(model_name: str, payload_context_window: int) -> int:
    """Prefer Guardian metadata when Claude Code reports a rounded default."""
    guardian_context_window = maybe_fetch_guardian_context(model_name)
    if guardian_context_window <= 0:
        return payload_context_window
    if payload_context_window <= 0:
        return guardian_context_window
    if abs(payload_context_window - guardian_context_window) >= CONTEXT_MISMATCH_TOLERANCE:
        return guardian_context_window
    return payload_context_window


def env_positive_int(name: str) -> int:
    """Return a positive integer environment variable, or zero when unset."""
    value = as_int(os.environ.get(name))
    return value if value > 0 else 0


def effective_context_window(model_name: str, payload_context_window: int) -> int:
    """Return the Claude-side window used for compaction and status display."""
    detected_context_window = choose_context_window(model_name, payload_context_window)
    requested_auto_compact_window = env_positive_int("CLAUDE_CODE_AUTO_COMPACT_WINDOW")
    if requested_auto_compact_window <= 0:
        return detected_context_window

    runtime_context_window = maybe_fetch_guardian_context(model_name, prefer_runtime=True)
    if runtime_context_window > 0:
        return min(requested_auto_compact_window, runtime_context_window)
    return requested_auto_compact_window


def format_tokens(value: int) -> str:
    """Format token counts into a compact human-readable string."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.0f}k"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


def auto_compact_percentage() -> int:
    """Return Claude's auto-compact percentage override or the default."""
    override = env_positive_int("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE")
    if 1 <= override <= 100:
        return override
    return DEFAULT_AUTO_COMPACT_PCT


def warning_threshold(context_window_size: int) -> int:
    """Return the token count at which Claude should auto-compact."""
    if context_window_size <= 0:
        return 0
    return max(int(context_window_size * auto_compact_percentage() / 100), 1)


def caution_threshold(compact_threshold: int) -> int:
    """Return the earlier warning threshold for rising context usage."""
    return max(int(compact_threshold * 0.85), 1)


def build_bar(used_percentage: int) -> str:
    """Build a simple ASCII progress bar."""
    clamped_percentage = max(0, min(used_percentage, 100))
    filled = clamped_percentage * BAR_WIDTH // 100
    empty = BAR_WIDTH - filled
    return f"[{'#' * filled}{'-' * empty}]"


def pick_status(input_tokens: int, context_window_size: int) -> tuple[str, str]:
    """Return the status label and ANSI color for the current context load."""
    compact_threshold = warning_threshold(context_window_size)
    if input_tokens >= compact_threshold:
        return "COMPACT SOON", ANSI_RED
    if input_tokens >= caution_threshold(compact_threshold):
        return "WATCH", ANSI_YELLOW
    return "OK", ANSI_GREEN


def main() -> int:
    """Render the status line to stdout."""
    payload = load_payload()

    model_info = payload.get("model") or {}
    workspace_info = payload.get("workspace") or {}
    context_info = payload.get("context_window") or {}

    model_name = model_info.get("display_name") or model_info.get("id") or "Claude"
    current_dir = workspace_info.get("current_dir") or payload.get("cwd") or os.getcwd()
    dir_name = os.path.basename(current_dir.rstrip(os.sep)) or current_dir

    input_tokens = as_int(context_info.get("total_input_tokens"))
    payload_context_window = as_int(context_info.get("context_window_size"))
    context_window_size = effective_context_window(model_name, payload_context_window)
    used_percentage = as_int(context_info.get("used_percentage"))
    if context_window_size > 0 and input_tokens > 0:
        used_percentage = max(0, min(int(round((input_tokens / context_window_size) * 100)), 100))
    remaining_tokens = max(context_window_size - input_tokens, 0) if context_window_size else 0
    compact_threshold = warning_threshold(context_window_size)

    status_label, status_color = pick_status(input_tokens, context_window_size)
    bar = build_bar(used_percentage)

    print(
        f"[{model_name}] {dir_name} | {status_color}{bar} {used_percentage}%{ANSI_RESET} "
        f"| {format_tokens(input_tokens)}/{format_tokens(context_window_size or 0)} "
        f"| left {format_tokens(remaining_tokens)} "
        f"| compact@{format_tokens(compact_threshold)} "
        f"| {status_color}{status_label}{ANSI_RESET}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())