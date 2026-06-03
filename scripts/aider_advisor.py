#!/usr/bin/env python3
"""Daily-gated OpenRouter GPT-5.5 Aider advisor lane for hard problems."""

from __future__ import annotations

import fcntl
import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
DEFAULT_ADVISOR_MODEL = "openrouter/openai/gpt-5.4"
DEFAULT_STATE_DIR = Path.home() / ".local" / "state" / "kyberm0nk"


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file without shell expansion."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value
    return values


def resolve_value(key: str, env_file_values: dict[str, str], default: str = "") -> str:
    """Return the first non-empty value from process env, .env, or default."""
    value = os.environ.get(key)
    if value:
        return value
    value = env_file_values.get(key)
    if value:
        return value
    return default


def resolve_secret(key: str, file_key: str, env_file_values: dict[str, str]) -> str:
    """Resolve a secret from an env var or a secret file path."""
    value = resolve_value(key, env_file_values, "")
    if value:
        return value

    file_path = resolve_value(file_key, env_file_values, "")
    if not file_path:
        return ""

    candidate = Path(file_path).expanduser()
    if not candidate.exists():
        return ""
    return candidate.read_text(encoding="utf-8").strip()


@contextmanager
def advisory_lock(lock_file: Path) -> Any:
    """Hold an advisory lock so only one advisor run can consume the daily slot."""
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_file.open("w", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def load_state(path: Path) -> dict[str, Any]:
    """Load advisor state from disk."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def save_state(path: Path, payload: dict[str, Any]) -> None:
    """Persist advisor state atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(path)


def resolve_aider_binary(aider_root: str, aider_venv_dir: str) -> str:
    """Resolve the aider binary path."""
    aider_bin = resolve_value("AIDER_BIN", env_values, "")
    if aider_bin:
        return aider_bin

    candidate = Path(aider_venv_dir).expanduser() / "bin" / "aider"
    if candidate.exists():
        return str(candidate)

    candidate = Path(aider_root).expanduser() / ".venv" / "bin" / "aider"
    if candidate.exists():
        return str(candidate)

    raise SystemExit(f"❌ ERROR: aider binary missing under {aider_venv_dir} or {aider_root}/.venv")


if not ENV_FILE.exists():
    raise SystemExit(f"❌ ERROR: .env file missing in {ROOT}")

env_values = parse_env_file(ENV_FILE)
active_project = resolve_value("ACTIVE_PROJECT", env_values, "")
if not active_project or not Path(active_project).is_dir():
    raise SystemExit(f"❌ ERROR: ACTIVE_PROJECT is not set or does not exist: {active_project}")

advisor_model = resolve_value("AIDER_ADVISOR_MODEL", env_values, DEFAULT_ADVISOR_MODEL)
advisor_state_dir = Path(
    resolve_value("AIDER_ADVISOR_STATE_DIR", env_values, str(DEFAULT_STATE_DIR))
).expanduser()
advisor_state_file = Path(
    resolve_value("AIDER_ADVISOR_STATE_FILE", env_values, str(advisor_state_dir / "aider_advisor.json"))
).expanduser()
lock_file = advisor_state_file.with_suffix(".lock")
dry_run = resolve_value("AIDER_ADVISOR_DRY_RUN", env_values, "false").strip().lower() in {"1", "true", "yes"}
force = resolve_value("AIDER_ADVISOR_FORCE", env_values, "false").strip().lower() in {"1", "true", "yes"}
today = datetime.now().date().isoformat()
now = datetime.now().astimezone().isoformat(timespec="seconds")

# Keep the existing Aider host-runtime convention for locating the binary.
aider_root = resolve_value("AIDER_ROOT", env_values, str(Path.home() / "aider"))
aider_venv_dir = resolve_value("AIDER_VENV_DIR", env_values, resolve_value("KYBER_AIDER_VENV_DIR", env_values, str(Path(aider_root) / ".venv")))
aider_bin = resolve_aider_binary(aider_root, aider_venv_dir)

with advisory_lock(lock_file):
    state = load_state(advisor_state_file)
    last_used_date = str(state.get("last_used_date") or "")
    last_used_at = str(state.get("last_used_at") or "")
    last_project = str(state.get("project") or "")
    last_model = str(state.get("model") or "")

    if last_used_date == today and not force:
        print(
            f"advisor skip: already used today ({last_used_at or last_used_date}) on {last_project or 'unknown project'} using {last_model or advisor_model}"
        )
        raise SystemExit(0)

    if dry_run:
        print(
            f"advisor dry-run: would use {advisor_model} once today for {active_project} via {aider_bin}"
        )
        raise SystemExit(0)

# OpenRouter routed through Aider needs OpenAI-compatible env vars on the real execution path.
openrouter_base = resolve_value("OPENROUTER_API_BASE", env_values, "https://openrouter.ai/api/v1")
openrouter_key = resolve_secret("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_FILE", env_values)
if not openrouter_key:
    raise SystemExit("❌ ERROR: OPENROUTER_API_KEY or OPENROUTER_API_KEY_FILE is missing")

save_state(
    advisor_state_file,
    {
        "last_used_date": today,
        "last_used_at": now,
        "model": advisor_model,
        "project": active_project,
        "command": [aider_bin, "--model", advisor_model, *sys.argv[1:]],
    },
)

child_env = os.environ.copy()
child_env["OPENAI_API_BASE"] = openrouter_base
child_env["OPENROUTER_API_BASE"] = openrouter_base
child_env["OPENAI_API_KEY"] = openrouter_key
child_env["OPENROUTER_API_KEY"] = openrouter_key
child_env.setdefault("ACTIVE_PROJECT", active_project)
child_env.setdefault("AIDER_ROOT", aider_root)
child_env.setdefault("AIDER_VENV_DIR", aider_venv_dir)
child_env.setdefault("KYBER_AIDER_VENV_DIR", aider_venv_dir)
child_env.setdefault("AIDER_ADVISOR_MODEL", advisor_model)

cmd = [
    aider_bin,
    "--model",
    advisor_model,
    "--no-auto-commits",
    "--no-git",
    "--yes",
    *sys.argv[1:],
]

os.execvpe(aider_bin, cmd, child_env)
