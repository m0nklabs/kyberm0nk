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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
INPUT_FIELDS = ("project_path", "operator_goal", "current_state", "operator_chat_guidance")
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
    state = load_state(project_id)
    if not state:
        return {
            "success": True,
            "project_id": project_id,
            "active": False,
            "status": "idle",
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

    inputs = argparse.ArgumentParser(add_help=False)
    inputs.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    inputs.add_argument("--output", choices=("text", "json"), default="text")
    inputs.add_argument("--project-path", default="")
    inputs.add_argument("--operator-goal", default="")
    inputs.add_argument("--current-state", default="")
    inputs.add_argument("--operator-chat-guidance", default="")

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
        kickoff_mode=args.kickoff_mode,
    )

    log(f"Starting CrewAI foreground run for {args.project_id} in {args.kickoff_mode} mode")
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
        kickoff_mode=args.kickoff_mode,
    )

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with LIVE_LOG_PATH.open("a", encoding="utf-8") as log_handle:
        log_handle.write(f"[{datetime.now(timezone.utc).isoformat()}] Starting background CrewAI run for {args.project_id} ({args.kickoff_mode})\n")

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