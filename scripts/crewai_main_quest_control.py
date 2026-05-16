#!/usr/bin/env python3
"""Control Kyber CrewAI main-quest runs with foreground and background modes."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIGS_DIR = REPO_ROOT / "configs" / "crewai"
LOGS_DIR = REPO_ROOT / "logs"
STATE_DIR = LOGS_DIR / "crewai_state"
LIVE_LOG_PATH = LOGS_DIR / "crewai_live.log"
DEFAULT_PROJECT_ID = "main_quest_project"
DEFAULT_WEB_CONTAINER = "crewai_studio_kyber"
DEFAULT_PROJECT_PATH = "/workspace/project/.agent-projects/NewNexus"
DEFAULT_OPERATOR_GOAL = "Create the first playable NewNexus Unreal slice."
DEFAULT_CURRENT_STATE = "NewNexus is the Unreal Engine project in m0nklabs/NewNexus."
DEFAULT_OPERATOR_CHAT_GUIDANCE = "Stay on Unreal Engine and NewNexus. Do not switch to Unity or generic 2D assumptions."
DEFAULT_REPO_WRITE_MODE = "disabled"
DEFAULT_GITHUB_TARGET_BRANCH = "main"
DEFAULT_GUARDIAN_IDLE_WAIT_SECONDS = 900.0
DEFAULT_GUARDIAN_IDLE_POLL_SECONDS = 2.0
DEFAULT_OPENROUTER_LOW_CREDIT_THRESHOLD_USD = 15.0
DEFAULT_OPENROUTER_CRITICAL_CREDIT_THRESHOLD_USD = 5.0
INPUT_FIELDS = (
    "project_path",
    "operator_goal",
    "current_state",
    "operator_chat_guidance",
    "repo_write_mode",
    "github_target_branch",
)
STOP_WAIT_SECONDS = 8.0


def load_env_file(path: Path) -> dict[str, str]:
    """Load a simple KEY=VALUE env file."""
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_controller_env() -> dict[str, str]:
    """Load host and CrewAI-Studio environment values used by the controller."""
    combined = load_env_file(REPO_ROOT / ".agent-projects" / "CrewAI-Studio" / ".env")
    combined.update(load_env_file(REPO_ROOT / ".env"))
    return combined


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file into a mapping, returning an empty mapping on blank files."""
    if not path.exists():
        raise FileNotFoundError(f"Missing YAML config: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def read_secret_value(path: str) -> str:
    """Read a secret string from a file path."""
    return Path(path).read_text(encoding="utf-8").strip()


def resolve_runtime_secret(root_env: dict[str, str], env_name: str, file_env_name: str | None = None) -> str:
    """Resolve a secret from process env, repo env, or an optional file pointer."""
    direct_value = os.environ.get(env_name) or root_env.get(env_name, "")
    if direct_value:
        return direct_value
    if not file_env_name:
        return ""
    file_path = os.environ.get(file_env_name) or root_env.get(file_env_name, "")
    if not file_path:
        return ""
    secret_path = Path(file_path).expanduser()
    if not secret_path.exists():
        return ""
    return read_secret_value(str(secret_path))


def normalize_local_api_base(api_base: str) -> str:
    """Normalize Docker-style local hostnames for host-side scripts."""
    return api_base.replace("host.docker.internal", "127.0.0.1")


def inspect_project_llm_usage(project_id: str) -> dict[str, Any]:
    """Summarize the providers and models required by a CrewAI project."""
    project_root = project_dir(project_id)
    crew_config = load_yaml_file(project_root / "crew.yaml")
    agent_config = load_yaml_file(project_root / "agents.yaml")

    llm_entries: list[dict[str, str]] = []

    def add_entry(role: str, provider: str | None, model: str | None) -> None:
        if not provider or not model:
            return
        llm_entries.append({
            "role": role,
            "provider": provider.strip().lower(),
            "model": model.strip(),
        })

    crew_block = crew_config.get("crew", {})
    manager = crew_block.get("manager_llm", {})
    planning = crew_block.get("planning_llm", {})
    if isinstance(manager, dict):
        add_entry("manager", manager.get("provider"), manager.get("model"))
    if isinstance(planning, dict):
        add_entry("planning", planning.get("provider"), planning.get("model"))

    for agent_name, agent_settings in (agent_config.get("agents", {}) or {}).items():
        if isinstance(agent_settings, dict):
            add_entry(agent_name, agent_settings.get("provider"), agent_settings.get("model"))

    provider_counts = Counter(entry["provider"] for entry in llm_entries)
    provider_models: dict[str, list[str]] = {}
    for entry in llm_entries:
        provider_models.setdefault(entry["provider"], []).append(entry["model"])

    for provider_name, models in provider_models.items():
        provider_models[provider_name] = sorted(set(models))

    return {
        "providers": sorted(provider_counts.keys()),
        "provider_counts": dict(sorted(provider_counts.items())),
        "provider_models": provider_models,
        "uses_guardian": "guardian" in provider_counts,
        "uses_openrouter": "openrouter" in provider_counts,
        "entries": llm_entries,
        "provider_settings": crew_config.get("providers", {}) or {},
    }


def guardian_status_url(api_base: str) -> str:
    """Convert an OpenAI-compatible Guardian base URL into the status endpoint."""
    normalized = normalize_local_api_base(api_base).rstrip("/")
    if normalized.endswith("/v1"):
        return f"{normalized[:-3]}/api/status"
    return f"{normalized}/api/status"


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout_seconds: float = 15.0) -> tuple[int, dict[str, Any]]:
    """Fetch JSON from an HTTP endpoint and return status plus payload."""
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status_code = getattr(response, "status", 200)
            payload = json.loads(response.read().decode("utf-8"))
            return status_code, payload if isinstance(payload, dict) else {"data": payload}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"error": body}
        return exc.code, payload if isinstance(payload, dict) else {"error": body}


def fetch_guardian_runtime_status(llm_usage: dict[str, Any]) -> dict[str, Any]:
    """Fetch Guardian runtime status for Guardian-backed CrewAI runs."""
    provider_settings = llm_usage.get("provider_settings", {}).get("guardian", {}) or {}
    controller_env = load_controller_env()
    api_base_env = provider_settings.get("api_base_env", "GUARDIAN_API_BASE")
    api_base = os.environ.get(api_base_env) or controller_env.get(api_base_env) or provider_settings.get("default_api_base", "")
    if not api_base:
        return {"success": False, "status": "unavailable", "message": "Guardian API base is not configured."}

    api_key_env = provider_settings.get("api_key_env", "GUARDIAN_API_KEY")
    api_key = resolve_runtime_secret(controller_env, api_key_env)
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    status_url = guardian_status_url(api_base)
    status_code, payload = fetch_json(status_url, headers=headers)
    if status_code != 200:
        return {
            "success": False,
            "status": "unavailable",
            "status_code": status_code,
            "status_url": status_url,
            "message": payload.get("detail") or payload.get("error") or "Failed to query Guardian status.",
        }

    queue = payload.get("queue", {}) or {}
    switch = payload.get("switch", {}) or {}
    startup = payload.get("startup", {}) or {}
    busy_reasons: list[str] = []
    if int(queue.get("active_count", 0) or 0) > 0:
        busy_reasons.append(f"active_requests={queue.get('active_count', 0)}")
    if int(queue.get("queue_length", 0) or 0) > 0:
        busy_reasons.append(f"queued_requests={queue.get('queue_length', 0)}")
    if bool(switch.get("active")):
        busy_reasons.append(f"switch={switch.get('phase') or switch.get('state')}")
    startup_state = str(startup.get("state") or "")
    if startup_state in {"pending", "checking", "switching", "running"}:
        busy_reasons.append(f"startup={startup_state}")

    return {
        "success": True,
        "status": "busy" if busy_reasons else "idle",
        "status_url": status_url,
        "busy_reasons": busy_reasons,
        "current_model": payload.get("current_model"),
        "queue": queue,
        "switch": switch,
        "startup": startup,
    }


def wait_for_guardian_idle(project_id: str, llm_usage: dict[str, Any], kickoff_mode: str) -> dict[str, Any]:
    """Wait until Guardian is idle before starting Guardian-backed live CrewAI runs."""
    if kickoff_mode != "live" or not llm_usage.get("uses_guardian"):
        return {
            "required": False,
            "status": "skipped",
            "message": "Guardian idle wait not required for this kickoff.",
        }

    timeout_seconds = float(os.environ.get("KYBER_CREWAI_GUARDIAN_IDLE_WAIT_SECONDS", DEFAULT_GUARDIAN_IDLE_WAIT_SECONDS))
    poll_seconds = float(os.environ.get("KYBER_CREWAI_GUARDIAN_IDLE_POLL_SECONDS", DEFAULT_GUARDIAN_IDLE_POLL_SECONDS))
    deadline = time.monotonic() + timeout_seconds
    first_busy_logged = False

    while True:
        status = fetch_guardian_runtime_status(llm_usage)
        if not status.get("success"):
            raise RuntimeError(
                f"Cannot verify Guardian availability before starting {project_id}: {status.get('message', 'unknown error')}"
            )
        if status.get("status") == "idle":
            waited_seconds = max(0.0, timeout_seconds - max(0.0, deadline - time.monotonic()))
            return {
                "required": True,
                "status": "ready",
                "waited_seconds": round(waited_seconds, 2),
                "current_model": status.get("current_model"),
                "busy_reasons": [],
                "status_url": status.get("status_url"),
                "message": "Guardian is idle; Guardian-backed CrewAI workers may start.",
            }

        if not first_busy_logged:
            log(
                "Guardian-backed CrewAI workers share the same local GPU route. "
                f"Waiting for Guardian to go idle before starting {project_id}: {', '.join(status.get('busy_reasons', []))}"
            )
            first_busy_logged = True

        if time.monotonic() >= deadline:
            raise RuntimeError(
                "Timed out waiting for Guardian to go idle before starting Guardian-backed CrewAI workers. "
                f"Still busy: {', '.join(status.get('busy_reasons', []))}"
            )
        time.sleep(poll_seconds)


def check_openrouter_credits(llm_usage: dict[str, Any], kickoff_mode: str) -> dict[str, Any]:
    """Check OpenRouter credit balance when a live run will spend cloud credits."""
    if kickoff_mode != "live" or not llm_usage.get("uses_openrouter"):
        return {
            "required": False,
            "status": "skipped",
            "message": "OpenRouter credit check not required for this kickoff.",
        }

    provider_settings = llm_usage.get("provider_settings", {}).get("openrouter", {}) or {}
    controller_env = load_controller_env()
    api_base_env = provider_settings.get("api_base_env", "OPENROUTER_API_BASE")
    api_key_env = provider_settings.get("api_key_env", "OPENROUTER_API_KEY")
    api_base = os.environ.get(api_base_env) or controller_env.get(api_base_env) or provider_settings.get("default_api_base", "https://openrouter.ai/api/v1")
    api_key = resolve_runtime_secret(controller_env, api_key_env, "OPENROUTER_API_KEY_FILE")
    if not api_key:
        return {
            "required": True,
            "status": "unavailable",
            "message": "OpenRouter-backed agents are configured, but no OpenRouter API key is available for a credit check.",
        }

    credits_url = f"{api_base.rstrip('/')}/credits"
    status_code, payload = fetch_json(
        credits_url,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if status_code != 200:
        message = payload.get("error", {}).get("message") if isinstance(payload.get("error"), dict) else payload.get("error")
        if not message:
            message = payload.get("message") or payload.get("detail") or "OpenRouter credit check unavailable."
        return {
            "required": True,
            "status": "unavailable",
            "status_code": status_code,
            "credits_url": credits_url,
            "message": (
                f"OpenRouter-backed agents will spend cloud credits, but the balance check is unavailable: {message}. "
                "Use a management key for automatic remaining-credit warnings."
            ),
        }

    data = payload.get("data", {}) or {}
    total_credits = float(data.get("total_credits", 0.0) or 0.0)
    total_usage = float(data.get("total_usage", 0.0) or 0.0)
    remaining_credits = total_credits - total_usage
    low_threshold = float(os.environ.get("OPENROUTER_LOW_CREDIT_THRESHOLD_USD", DEFAULT_OPENROUTER_LOW_CREDIT_THRESHOLD_USD))
    critical_threshold = float(os.environ.get("OPENROUTER_CRITICAL_CREDIT_THRESHOLD_USD", DEFAULT_OPENROUTER_CRITICAL_CREDIT_THRESHOLD_USD))

    if remaining_credits <= critical_threshold:
        status = "critical"
        message = (
            f"OpenRouter-backed agents will spend cloud credits and only about ${remaining_credits:.2f} remains. "
            "Top up credits now before starting another live run."
        )
    elif remaining_credits <= low_threshold:
        status = "low"
        message = (
            f"OpenRouter-backed agents will spend cloud credits and only about ${remaining_credits:.2f} remains. "
            "Plan a top-up soon."
        )
    else:
        status = "ok"
        message = f"OpenRouter credit balance looks healthy at about ${remaining_credits:.2f} remaining."

    return {
        "required": True,
        "status": status,
        "credits_url": credits_url,
        "total_credits": round(total_credits, 4),
        "total_usage": round(total_usage, 4),
        "remaining_credits": round(remaining_credits, 4),
        "low_threshold": low_threshold,
        "critical_threshold": critical_threshold,
        "message": message,
    }


def evaluate_kickoff_policies(project_id: str, kickoff_mode: str) -> dict[str, Any]:
    """Evaluate local-GPU and cloud-credit policies before a run starts."""
    llm_usage = inspect_project_llm_usage(project_id)
    guardian_local_policy = wait_for_guardian_idle(project_id, llm_usage, kickoff_mode)
    openrouter_credit_policy = check_openrouter_credits(llm_usage, kickoff_mode)
    if openrouter_credit_policy.get("required"):
        log(openrouter_credit_policy.get("message", "OpenRouter credit status checked."))
    return {
        "llm_usage": {
            "providers": llm_usage.get("providers", []),
            "provider_counts": llm_usage.get("provider_counts", {}),
            "provider_models": llm_usage.get("provider_models", {}),
            "uses_guardian": llm_usage.get("uses_guardian", False),
            "uses_openrouter": llm_usage.get("uses_openrouter", False),
        },
        "guardian_local_policy": guardian_local_policy,
        "openrouter_credit_policy": openrouter_credit_policy,
    }


def log(message: str) -> None:
    """Print a timestamped control message."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] {message}")


def json_output(payload: dict[str, Any]) -> None:
    """Write one JSON payload to stdout."""
    print(json.dumps(payload, indent=2, sort_keys=True))


def project_dir(project_id: str) -> Path:
    """Return the tracked CrewAI project directory."""
    path = CONFIGS_DIR / project_id
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Unknown CrewAI project id: {project_id}")
    return path


def project_target(project_id: str) -> str:
    """Return the container-side path for a CrewAI project copy."""
    return f"/tmp/kyber-{project_id.replace('_', '-') }"


def state_path(project_id: str) -> Path:
    """Return the persisted controller state path for a project."""
    return STATE_DIR / f"{project_id}.json"


def default_operator_inputs() -> dict[str, str]:
    """Return the default operator inputs for the tracked main quest."""
    return {
        "project_path": DEFAULT_PROJECT_PATH,
        "operator_goal": DEFAULT_OPERATOR_GOAL,
        "current_state": DEFAULT_CURRENT_STATE,
        "operator_chat_guidance": DEFAULT_OPERATOR_CHAT_GUIDANCE,
        "repo_write_mode": DEFAULT_REPO_WRITE_MODE,
        "github_target_branch": DEFAULT_GITHUB_TARGET_BRANCH,
    }


def load_runtime_settings() -> dict[str, str]:
    """Load runtime settings from repo and optional Studio env files."""
    root_env = load_env_file(REPO_ROOT / ".env")
    studio_dir = Path(root_env.get("CREWAI_STUDIO_DIR", REPO_ROOT / ".agent-projects" / "CrewAI-Studio"))
    studio_env = load_env_file(studio_dir / ".env")
    container_name = studio_env.get("CREWAI_STUDIO_WEB_CONTAINER") or root_env.get("CREWAI_STUDIO_WEB_CONTAINER") or DEFAULT_WEB_CONTAINER
    return {
        "crewai_studio_dir": str(studio_dir),
        "crewai_studio_web_container": container_name,
    }


def run_command(command: list[str], capture_output: bool = True, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command."""
    return subprocess.run(
        command,
        check=False,
        capture_output=capture_output,
        text=True,
        timeout=timeout_seconds,
    )


def ensure_container_running(container_name: str) -> None:
    """Ensure the CrewAI Studio web container exists and is running."""
    result = run_command(["docker", "inspect", "-f", "{{.State.Running}}", container_name], timeout_seconds=20)
    if result.returncode != 0 or result.stdout.strip().lower() != "true":
        detail = (result.stderr or result.stdout).strip() or "container not running"
        raise RuntimeError(f"CrewAI-Studio container {container_name} is not available: {detail}")


def stage_project_copy(container_name: str, project_id: str) -> str:
    """Copy the tracked project into the Studio container."""
    source = project_dir(project_id)
    target = project_target(project_id)
    remove_result = run_command(["docker", "exec", container_name, "rm", "-rf", target], timeout_seconds=60)
    if remove_result.returncode != 0:
        detail = (remove_result.stderr or remove_result.stdout).strip()
        raise RuntimeError(f"Failed to clear project target {target}: {detail}")

    copy_result = run_command(["docker", "cp", str(source), f"{container_name}:{target}"], timeout_seconds=120)
    if copy_result.returncode != 0:
        detail = (copy_result.stderr or copy_result.stdout).strip()
        raise RuntimeError(f"Failed to copy project into container: {detail}")
    return target


def build_crew_command(
    container_name: str,
    container_project_target: str,
    project_path: str,
    operator_goal: str,
    current_state: str,
    operator_chat_guidance: str,
    repo_write_mode: str,
    github_target_branch: str,
    kickoff_mode: str,
) -> list[str]:
    """Build the docker exec command for the CrewAI project."""
    command = [
        "docker",
        "exec",
        container_name,
        "python",
        f"{container_project_target}/crew.py",
        "--project-path",
        project_path,
        "--operator-goal",
        operator_goal,
        "--current-state",
        current_state,
        "--operator-chat-guidance",
        operator_chat_guidance,
        "--repo-write-mode",
        repo_write_mode,
        "--github-target-branch",
        github_target_branch,
    ]
    if kickoff_mode == "dry_run":
        command.append("--dry-run")
    return command


def load_state(project_id: str) -> dict[str, Any]:
    """Load the persisted controller state."""
    path = state_path(project_id)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def extract_operator_inputs(state: dict[str, Any]) -> dict[str, str]:
    """Extract operator input fields from persisted state."""
    return {
        field: str(state.get(field, "") or "")
        for field in INPUT_FIELDS
    }


def kickoff_overrides_from_args(args: argparse.Namespace) -> dict[str, str]:
    """Extract non-empty operator input overrides from parsed args."""
    return {
        field: str(getattr(args, field, "") or "")
        for field in INPUT_FIELDS
    }


def resolve_operator_inputs(project_id: str, overrides: dict[str, str] | None = None) -> dict[str, str]:
    """Resolve operator inputs from defaults, persisted state, and explicit overrides."""
    resolved = default_operator_inputs()
    saved_state = load_state(project_id)
    saved_inputs = extract_operator_inputs(saved_state)
    resolved.update({key: value for key, value in saved_inputs.items() if value})
    resolved.update({key: value for key, value in (overrides or {}).items() if value})
    return resolved


def update_operator_inputs(project_id: str, overrides: dict[str, str]) -> dict[str, Any]:
    """Persist operator input overrides for a project and return the merged payload."""
    state = load_state(project_id)
    state.setdefault("project_id", project_id)
    state.setdefault("status", state.get("status", "idle") or "idle")
    merged_inputs = resolve_operator_inputs(project_id, overrides)
    state.update(merged_inputs)
    state["operator_inputs_updated_at"] = datetime.now(timezone.utc).isoformat()
    save_state(project_id, state)
    return {
        "success": True,
        "project_id": project_id,
        "status": state.get("status", "idle"),
        "active": build_status_payload(project_id).get("active", False),
        "operator_inputs": merged_inputs,
        "message": "Operator inputs updated.",
    }


def save_state(project_id: str, payload: dict[str, Any]) -> None:
    """Persist the controller state as JSON."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with state_path(project_id).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def get_process_args(pid: int) -> str:
    """Return the process args for a PID or an empty string."""
    result = run_command(["ps", "-p", str(pid), "-o", "args="], timeout_seconds=10)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def is_pid_active(pid: int | None, command_signature: str) -> bool:
    """Return whether a PID is active and still matches the expected command."""
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    args = get_process_args(pid)
    return bool(args and command_signature in args)


def build_status_payload(project_id: str) -> dict[str, Any]:
    """Build the current controller status for a project."""
    llm_usage = inspect_project_llm_usage(project_id)
    default_guardian_policy = {
        "status": "unknown",
        "message": "No persisted Guardian kickoff policy is available for this run yet.",
    }
    default_openrouter_policy = {
        "status": "unknown",
        "message": "No persisted OpenRouter credit policy is available for this run yet.",
    }
    state = load_state(project_id)
    if not state:
        return {
            "success": True,
            "project_id": project_id,
            "active": False,
            "status": "idle",
            "llm_usage": {
                "providers": llm_usage.get("providers", []),
                "provider_counts": llm_usage.get("provider_counts", {}),
                "provider_models": llm_usage.get("provider_models", {}),
                "uses_guardian": llm_usage.get("uses_guardian", False),
                "uses_openrouter": llm_usage.get("uses_openrouter", False),
            },
            "guardian_local_policy": default_guardian_policy,
            "openrouter_credit_policy": default_openrouter_policy,
            "operator_inputs": default_operator_inputs(),
            "state_path": str(state_path(project_id)),
        }

    command_signature = state.get("command_signature", project_target(project_id))
    pid = int(state.get("pid", 0) or 0)
    active = is_pid_active(pid, command_signature)
    if state.get("status") == "running" and not active:
        state["status"] = "exited"
        state["exited_at"] = datetime.now(timezone.utc).isoformat()
        save_state(project_id, state)

    return {
        "success": True,
        "project_id": project_id,
        "active": active,
        "status": state.get("status", "unknown"),
        "llm_usage": {
            "providers": llm_usage.get("providers", []),
            "provider_counts": llm_usage.get("provider_counts", {}),
            "provider_models": llm_usage.get("provider_models", {}),
            "uses_guardian": llm_usage.get("uses_guardian", False),
            "uses_openrouter": llm_usage.get("uses_openrouter", False),
        },
        "guardian_local_policy": state.get("guardian_local_policy", default_guardian_policy),
        "openrouter_credit_policy": state.get("openrouter_credit_policy", default_openrouter_policy),
        "operator_inputs": resolve_operator_inputs(project_id),
        "state_path": str(state_path(project_id)),
        **state,
    }


def stop_active_run(project_id: str, force: bool = False) -> dict[str, Any]:
    """Stop the active background run for a project if one exists."""
    state = load_state(project_id)
    if not state:
        return {
            "success": True,
            "project_id": project_id,
            "active": False,
            "status": "idle",
            "message": "No persisted run state exists.",
        }

    pid = int(state.get("pid", 0) or 0)
    command_signature = state.get("command_signature", project_target(project_id))
    active = is_pid_active(pid, command_signature)
    if not active:
        state["status"] = "exited"
        state["stopped_at"] = datetime.now(timezone.utc).isoformat()
        save_state(project_id, state)
        return {
            "success": True,
            "project_id": project_id,
            "active": False,
            "status": state["status"],
            "message": "No active background run was found.",
        }

    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        active = False
    else:
        deadline = time.monotonic() + STOP_WAIT_SECONDS
        while time.monotonic() < deadline:
            if not is_pid_active(pid, command_signature):
                active = False
                break
            time.sleep(0.25)

    if active and force:
        os.killpg(pid, signal.SIGKILL)
        active = is_pid_active(pid, command_signature)

    runtime = load_runtime_settings()
    container_name = state.get("container_name") or runtime["crewai_studio_web_container"]
    if active:
        run_command(
            ["docker", "exec", container_name, "pkill", "-f", f"{project_target(project_id)}/crew.py"],
            timeout_seconds=20,
        )
        active = is_pid_active(pid, command_signature)

    state["status"] = "stopped" if not active else "stop_failed"
    state["stopped_at"] = datetime.now(timezone.utc).isoformat()
    save_state(project_id, state)

    return {
        "success": not active,
        "project_id": project_id,
        "active": active,
        "status": state["status"],
        "message": "Background run stopped." if not active else "Failed to stop background run cleanly.",
        "pid": pid,
    }


def parse_args() -> argparse.Namespace:
    """Parse control-script arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    common.add_argument("--output", choices=("text", "json"), default="text")

    kickoff = argparse.ArgumentParser(add_help=False)
    kickoff.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    kickoff.add_argument("--output", choices=("text", "json"), default="text")
    kickoff.add_argument("--kickoff-mode", choices=("live", "dry_run"), default="live")
    kickoff.add_argument("--project-path", default="")
    kickoff.add_argument("--operator-goal", default="")
    kickoff.add_argument("--current-state", default="")
    kickoff.add_argument("--operator-chat-guidance", default="")
    kickoff.add_argument("--repo-write-mode", choices=("disabled", "enabled"), default="")
    kickoff.add_argument("--github-target-branch", default="")

    inputs = argparse.ArgumentParser(add_help=False)
    inputs.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    inputs.add_argument("--output", choices=("text", "json"), default="text")
    inputs.add_argument("--project-path", default="")
    inputs.add_argument("--operator-goal", default="")
    inputs.add_argument("--current-state", default="")
    inputs.add_argument("--operator-chat-guidance", default="")
    inputs.add_argument("--repo-write-mode", choices=("disabled", "enabled"), default="")
    inputs.add_argument("--github-target-branch", default="")

    subparsers.add_parser("run", parents=[kickoff], help="Run the CrewAI project in the foreground.")
    subparsers.add_parser("start", parents=[kickoff], help="Start the CrewAI project in the background.")
    restart_parser = subparsers.add_parser("restart", parents=[kickoff], help="Restart the CrewAI project in the background.")
    restart_parser.add_argument("--force", action="store_true")
    subparsers.add_parser("status", parents=[common], help="Show background-run status.")
    subparsers.add_parser("get-inputs", parents=[common], help="Show persisted operator inputs.")
    subparsers.add_parser("set-inputs", parents=[inputs], help="Update persisted operator inputs.")
    stop_parser = subparsers.add_parser("stop", parents=[common], help="Stop the active background run.")
    stop_parser.add_argument("--force", action="store_true")

    return parser.parse_args()


def emit(payload: dict[str, Any], output_mode: str) -> int:
    """Emit structured or textual output and return an exit code."""
    if output_mode == "json":
        json_output(payload)
        return 0 if payload.get("success", False) else 1

    for key, value in payload.items():
        print(f"{key}: {value}")
    return 0 if payload.get("success", False) else 1


def run_foreground(args: argparse.Namespace) -> int:
    """Run the CrewAI project in the foreground with inherited stdio."""
    guardrails = evaluate_kickoff_policies(args.project_id, args.kickoff_mode)
    runtime = load_runtime_settings()
    container_name = runtime["crewai_studio_web_container"]
    ensure_container_running(container_name)
    target = stage_project_copy(container_name, args.project_id)
    operator_inputs = resolve_operator_inputs(args.project_id, kickoff_overrides_from_args(args))
    command = build_crew_command(
        container_name=container_name,
        container_project_target=target,
        project_path=operator_inputs["project_path"],
        operator_goal=operator_inputs["operator_goal"],
        current_state=operator_inputs["current_state"],
        operator_chat_guidance=operator_inputs["operator_chat_guidance"],
        repo_write_mode=operator_inputs["repo_write_mode"],
        github_target_branch=operator_inputs["github_target_branch"],
        kickoff_mode=args.kickoff_mode,
    )

    log(f"Starting CrewAI foreground run for {args.project_id} in {args.kickoff_mode} mode")
    log(f"Kickoff policy summary: {json.dumps(guardrails, sort_keys=True)}")
    result = subprocess.run(command, check=False)
    return result.returncode


def start_background(args: argparse.Namespace) -> dict[str, Any]:
    """Start the CrewAI project in the background and persist controller state."""
    current = build_status_payload(args.project_id)
    if current.get("active"):
        return {
            "success": True,
            "project_id": args.project_id,
            "message": "A background run is already active.",
            **current,
        }

    guardrails = evaluate_kickoff_policies(args.project_id, args.kickoff_mode)
    runtime = load_runtime_settings()
    container_name = runtime["crewai_studio_web_container"]
    ensure_container_running(container_name)
    target = stage_project_copy(container_name, args.project_id)
    operator_inputs = resolve_operator_inputs(args.project_id, kickoff_overrides_from_args(args))
    command = build_crew_command(
        container_name=container_name,
        container_project_target=target,
        project_path=operator_inputs["project_path"],
        operator_goal=operator_inputs["operator_goal"],
        current_state=operator_inputs["current_state"],
        operator_chat_guidance=operator_inputs["operator_chat_guidance"],
        repo_write_mode=operator_inputs["repo_write_mode"],
        github_target_branch=operator_inputs["github_target_branch"],
        kickoff_mode=args.kickoff_mode,
    )

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LIVE_LOG_PATH.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"[{datetime.now(timezone.utc).isoformat()}] Starting background CrewAI run for {args.project_id} ({args.kickoff_mode})\n")
        log_handle.write(f"[{datetime.now(timezone.utc).isoformat()}] Kickoff policy summary: {json.dumps(guardrails, sort_keys=True)}\n")

    log_stream = LIVE_LOG_PATH.open("a", encoding="utf-8")
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log_stream,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        text=True,
    )
    log_stream.close()

    payload = {
        "project_id": args.project_id,
        "status": "running",
        "pid": process.pid,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "kickoff_mode": args.kickoff_mode,
        **operator_inputs,
        "container_name": container_name,
        "container_project_target": target,
        "command_signature": target,
        **guardrails,
    }
    save_state(args.project_id, payload)
    return {
        "success": True,
        "active": True,
        "message": "Background run started.",
        **payload,
    }


def restart_background(args: argparse.Namespace) -> dict[str, Any]:
    """Restart the CrewAI project in the background using merged operator inputs."""
    previous = stop_active_run(args.project_id, force=args.force)
    started = start_background(args)
    started["previous_status"] = previous.get("status", "idle")
    started["message"] = "Background run restarted."
    return started


def main() -> int:
    """CLI entry point for run control."""
    args = parse_args()

    try:
        project_dir(args.project_id)
        if args.command == "run":
            return run_foreground(args)
        if args.command == "start":
            return emit(start_background(args), args.output)
        if args.command == "restart":
            return emit(restart_background(args), args.output)
        if args.command == "status":
            return emit(build_status_payload(args.project_id), args.output)
        if args.command == "get-inputs":
            return emit({
                "success": True,
                "project_id": args.project_id,
                "operator_inputs": resolve_operator_inputs(args.project_id),
                "active": build_status_payload(args.project_id).get("active", False),
            }, args.output)
        if args.command == "set-inputs":
            return emit(update_operator_inputs(args.project_id, kickoff_overrides_from_args(args)), args.output)
        if args.command == "stop":
            return emit(stop_active_run(args.project_id, force=args.force), args.output)
    except Exception as exc:
        return emit(
            {
                "success": False,
                "project_id": getattr(args, "project_id", DEFAULT_PROJECT_ID),
                "error": str(exc),
            },
            getattr(args, "output", "text"),
        )

    return 64


if __name__ == "__main__":
    raise SystemExit(main())