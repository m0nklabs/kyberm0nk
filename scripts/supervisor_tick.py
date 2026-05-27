#!/usr/bin/env python3
"""Run one bounded supervisor decision tick for a local coding worker."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlparse, urlunparse


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_PATH = REPO_ROOT / "logs" / "supervisor" / "supervisor_tick.jsonl"
DEFAULT_ENV_PATH = REPO_ROOT / ".env"
DEFAULT_API_BASE = "http://127.0.0.1:11434/v1"
DEFAULT_MODEL = "qwen3-35b-reasoning-agent"
DEFAULT_PROTECTED_PATTERNS = [
    r"(^|/)\.env($|\.)",
    r"(^|/)\.secrets(/|$)",
    r"(^|/)config/api_keys\.json$",
    r"(^|/)configs/ssh(/|$)",
    r"(^|/)docker-compose\.ya?ml$",
    r"(^|/)\.github/",
    r"(^|/)memories/",
]
FAILURE_PATTERN = re.compile(r"\b(fail(?:ed|ure)?|error|traceback|exception|fatal)\b", re.IGNORECASE)
SUCCESS_PATTERN = re.compile(r"\b(pass(?:ed)?|success|succeeded|ok)\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="Repository path to inspect.")
    parser.add_argument("--context-file", type=Path, help="Optional JSON file containing worker context.")
    parser.add_argument("--validation-file", type=Path, help="Optional build/test output file to summarize.")
    parser.add_argument("--worker-id", default="local-worker", help="Worker context identifier.")
    parser.add_argument("--worker-kind", default="opencode", help="Worker type or runtime.")
    parser.add_argument("--worker-name", default="", help="Human-readable worker name.")
    parser.add_argument("--failure-count", type=int, default=0, help="Known repeated failure count for the active task.")
    parser.add_argument("--task", default="", help="Short task summary for the active worker.")
    parser.add_argument("--max-diff-chars", type=int, default=5000, help="Maximum diff preview characters to include.")
    parser.add_argument("--max-validation-chars", type=int, default=3000, help="Maximum validation output characters to include.")
    parser.add_argument("--protected-path", action="append", default=[], help="Additional regex for protected paths.")
    parser.add_argument("--heuristic-only", action="store_true", help="Skip Guardian and return only the local heuristic decision.")
    parser.add_argument("--api-base", default=None, help="Guardian OpenAI-compatible base URL.")
    parser.add_argument("--api-key", default=None, help="Guardian API key.")
    parser.add_argument("--model", default=None, help="Guardian model alias for the critic.")
    parser.add_argument("--output", choices=("text", "json"), default="json", help="Output format.")
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="JSONL log path for decisions.")
    return parser.parse_args()


def load_env_file(path: Path) -> dict[str, str]:
    """Load a simple KEY=VALUE env file."""
    if not path.exists():
        return {}

    env: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def normalize_api_base(api_base: str) -> str:
    """Normalize Guardian base URLs across host and container contexts."""
    parsed = urlparse(api_base)
    if parsed.hostname != "host.docker.internal":
        return api_base

    try:
        socket.gethostbyname(parsed.hostname)
        return api_base
    except OSError:
        replacement = parsed._replace(netloc=parsed.netloc.replace("host.docker.internal", "127.0.0.1"))
        return urlunparse(replacement)


def run_git(repo: Path, *args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def load_context(path: Path | None) -> dict[str, Any]:
    """Load optional worker context JSON."""
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Context file {path} did not contain a JSON object.")
    return payload


def read_text_preview(path: Path | None, char_limit: int) -> str:
    """Read a bounded preview from a text file."""
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:char_limit]


def classify_validation(text: str) -> str:
    """Classify validation output coarsely."""
    if not text.strip():
        return "unknown"
    if FAILURE_PATTERN.search(text):
        return "failed"
    if SUCCESS_PATTERN.search(text):
        return "passed"
    return "unknown"


def changed_files_from_status(status_text: str) -> list[str]:
    """Extract changed file paths from `git status --short` output."""
    files: list[str] = []
    for line in status_text.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            files.append(path)
    return files


def heuristic_decision(summary: dict[str, Any], protected_patterns: list[str]) -> dict[str, Any]:
    """Return a bounded local decision before or instead of Guardian."""
    changed_files = summary["repo"]["changed_files"]
    failure_count = summary["worker"]["failure_count"]
    validation_status = summary["validation"]["status"]

    protected_hits = [
        path
        for path in changed_files
        if any(re.search(pattern, path) for pattern in protected_patterns)
    ]
    if protected_hits:
        return {
            "action": "stop",
            "confidence": 0.98,
            "message": f"Protected paths touched: {', '.join(protected_hits[:5])}. Stop and review scope.",
            "reason": "The worker modified protected paths that need explicit review.",
            "escalation_reason": "",
            "source": "heuristic",
        }

    if validation_status == "failed" and failure_count >= 2:
        return {
            "action": "escalate",
            "confidence": 0.9,
            "message": "The same task has failed repeatedly. Escalate for stronger review.",
            "reason": "Repeated validation failures crossed the local escalation threshold.",
            "escalation_reason": "Repeated validation failures",
            "source": "heuristic",
        }

    if validation_status == "failed":
        return {
            "action": "nudge",
            "confidence": 0.72,
            "message": "Validation failed. Fix the current slice and rerun the same check before widening scope.",
            "reason": "The current change slice still has a local validation failure.",
            "escalation_reason": "",
            "source": "heuristic",
        }

    if not changed_files:
        return {
            "action": "continue",
            "confidence": 0.66,
            "message": "",
            "reason": "No pending repository changes are visible in the current worker slice.",
            "escalation_reason": "",
            "source": "heuristic",
        }

    return {
        "action": "continue",
        "confidence": 0.6,
        "message": "",
        "reason": "No protected-path hits or repeated validation failures were detected locally.",
        "escalation_reason": "",
        "source": "heuristic",
    }


def build_summary(args: argparse.Namespace, context: dict[str, Any]) -> dict[str, Any]:
    """Collect the bounded repo and worker state used by the critic."""
    repo = args.repo.resolve()
    status_text = run_git(repo, "status", "--short")
    changed_files = changed_files_from_status(status_text)
    diff_stat = run_git(repo, "diff", "--stat")
    diff_preview = run_git(repo, "diff", "--no-color", "--unified=0")[: args.max_diff_chars]
    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    validation_preview = read_text_preview(args.validation_file, args.max_validation_chars)
    validation_status = classify_validation(validation_preview)

    worker = {
        "worker_id": context.get("worker_id", args.worker_id),
        "worker_kind": context.get("worker_kind", args.worker_kind),
        "worker_name": context.get("worker_name", args.worker_name),
        "failure_count": int(context.get("failure_count", args.failure_count)),
        "task": context.get("task", args.task),
        "notes": context.get("notes", ""),
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": {
            "path": str(repo),
            "branch": branch,
            "changed_files": changed_files,
            "status": status_text,
            "diff_stat": diff_stat,
            "diff_preview": diff_preview,
        },
        "worker": worker,
        "validation": {
            "path": str(args.validation_file) if args.validation_file else "",
            "status": validation_status,
            "preview": validation_preview,
        },
    }


def guardian_decision(summary: dict[str, Any], api_base: str, api_key: str, model: str) -> dict[str, Any]:
    """Ask Guardian for the bounded supervisor decision."""
    system_prompt = (
        "You are a strict supervisor critic for a local coding worker. "
        "Return only JSON with keys action, confidence, message, reason, escalation_reason. "
        "Allowed actions: continue, nudge, stop, escalate. "
        "Use short operational messages. "
        "Prefer continue when safe progress is still happening, nudge for local repair, "
        "stop for unsafe edits, and escalate for repeated failure or unclear architecture."
    )
    user_prompt = json.dumps(summary, indent=2)
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{api_base.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Guardian critic call failed: HTTP {exc.code} {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Guardian critic call failed: {exc}") from exc

    content = raw["choices"][0]["message"].get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Guardian critic returned no text content.")

    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError(f"Guardian critic did not return JSON: {content}")

    decision = json.loads(content[start : end + 1])
    decision["source"] = "guardian"
    return decision


def append_log(path: Path, payload: dict[str, Any]) -> None:
    """Append one JSONL decision record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def render_text(decision: dict[str, Any], summary: dict[str, Any]) -> str:
    """Render a concise human-readable supervisor result."""
    return "\n".join(
        [
            "Supervisor tick result",
            f"- Repo: {summary['repo']['path']}",
            f"- Branch: {summary['repo']['branch']}",
            f"- Worker: {summary['worker']['worker_kind']} ({summary['worker']['worker_id']})",
            f"- Action: {decision['action']}",
            f"- Confidence: {decision['confidence']}",
            f"- Source: {decision.get('source', 'unknown')}",
            f"- Reason: {decision['reason']}",
            f"- Message: {decision['message']}",
        ]
    )


def main() -> int:
    """Run one supervisor decision tick."""
    args = parse_args()
    env = load_env_file(DEFAULT_ENV_PATH)
    context = load_context(args.context_file)
    summary = build_summary(args, context)

    protected_patterns = DEFAULT_PROTECTED_PATTERNS + list(args.protected_path)
    local_decision = heuristic_decision(summary, protected_patterns)

    if args.heuristic_only or local_decision["action"] == "stop":
        decision = local_decision
    else:
        api_base = args.api_base or env.get("GUARDIAN_BASE_URL") or os.environ.get("GUARDIAN_BASE_URL") or DEFAULT_API_BASE
        api_base = normalize_api_base(api_base)
        api_key = args.api_key or env.get("KYBERM0NK_GUARDIAN_API_KEY") or os.environ.get("KYBERM0NK_GUARDIAN_API_KEY") or "local-dev"
        model = args.model or env.get("SUPERVISOR_MODEL") or os.environ.get("SUPERVISOR_MODEL") or env.get("DEFAULT_MODEL") or os.environ.get("DEFAULT_MODEL") or DEFAULT_MODEL
        try:
            decision = guardian_decision(summary, api_base, api_key, model)
        except Exception as exc:
            decision = {
                "action": "escalate",
                "confidence": 0.5,
                "message": "Local critic call failed. Escalate or rerun once Guardian is healthy.",
                "reason": str(exc),
                "escalation_reason": "Guardian critic unavailable",
                "source": "fallback",
            }

    record = {
        "timestamp": summary["timestamp"],
        "repo": summary["repo"],
        "worker": summary["worker"],
        "validation": summary["validation"],
        "decision": decision,
    }
    append_log(args.log_path, record)

    if args.output == "json":
        print(json.dumps(record, indent=2, sort_keys=True))
    else:
        print(render_text(decision, summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())