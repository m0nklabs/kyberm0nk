"""KyberM0nk pipeline orchestrator.

Pipeline:
    operator goal --> OpenCode (Strategist) --> plan --> Agent Zero (Executor) --> result

In v1 both roles are run by `interpreter` (open-interpreter) with different
system prompts, because Agent Zero's full integration (web UI + settings +
Guardian model routing) is a follow-up. Agent Zero stays installed and
launchable on its own. Aider stays installed for surgical edits.

Usage (inside sandbox):
    python -m cockpit.pipeline run "make a hello world script"
    python -m cockpit.pipeline run --no-execute "research topic X"
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

GUARDIAN_BASE_URL = os.environ.get("OPENAI_API_BASE", "http://host.docker.internal:11434/v1")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "qwen3-35b-uncensored")
JOBS_DIR = Path(os.environ.get("COCKPIT_JOBS_DIR", "/logs/jobs"))

PLANNER_SYSTEM = """You are OpenCode, the Strategist of the KyberM0nk cockpit.

Your single job is to convert one operator goal into a concrete, numbered
execution plan for an autonomous executor (Agent Zero / interpreter).

Rules:
- Do NOT execute code. Only plan.
- Be specific: name files, commands, verification steps.
- Identify external resources the executor will need (gh, curl, search,
  filesystem). The executor has /workspace/project (rw), /config (rw),
  /logs (rw), and the sandbox's full toolchain (gh, git, curl,
  playwright, python, node).
- End with a section titled "HANDOFF PROMPT FOR EXECUTOR:" containing
  the exact instructions the executor will receive verbatim.

Output Markdown only. No code execution.
"""

EXECUTOR_SYSTEM = """You are Agent Zero, the autonomous Executor inside the
KyberM0nk sandbox.

You receive a plan from the Strategist. Execute it. You may use the shell,
gh, git, curl, python, node, playwright, and the filesystem under
/workspace and /config. Network is available. Report progress
continuously and stop only when done or genuinely blocked.

Be autonomous. Do not ask the operator for clarification mid-flight unless
absolutely necessary.
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_role(role: str, system: str, prompt: str, model: str, job_dir: Path,
             auto_run: bool) -> tuple[int, str]:
    """Invoke `interpreter` for one role, stream output to stdout + file."""
    log_path = job_dir / f"{role}.log"
    cmd = [
        "interpreter",
        "--model", f"openai/{model}",
        "--api_base", GUARDIAN_BASE_URL,
        "--disable_telemetry",
        "--system_message", system,
    ]
    if auto_run:
        cmd.append("--auto_run")

    banner = f"\n=== [{role}] {now()} model={model} ===\n$ {' '.join(shlex.quote(c) for c in cmd)}\n"
    print(banner, end="", flush=True)

    chunks: list[str] = []
    with log_path.open("w") as logf:
        logf.write(banner)
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdin and proc.stdout
        proc.stdin.write(prompt + "\n")
        proc.stdin.close()
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            logf.write(line)
            chunks.append(line)
        rc = proc.wait()
    return rc, "".join(chunks)


def cmd_run(args: argparse.Namespace) -> int:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    job_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "id": job_id,
        "goal": args.goal,
        "model": args.model,
        "created_at": now(),
        "auto_execute": not args.no_execute,
    }
    (job_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    (job_dir / "goal.txt").write_text(args.goal)

    print(f"[kyberm0nk] job_id={job_id} dir={job_dir}")

    planner_prompt = (
        f"OPERATOR GOAL:\n{args.goal}\n\n"
        "Produce the plan now. Do not run code."
    )
    rc, plan_text = run_role(
        role="planner",
        system=PLANNER_SYSTEM,
        prompt=planner_prompt,
        model=args.model,
        job_dir=job_dir,
        auto_run=False,
    )
    (job_dir / "plan.md").write_text(plan_text)
    if rc != 0:
        print(f"[kyberm0nk] planner exited {rc}", file=sys.stderr)
        return rc

    if args.no_execute:
        print(f"[kyberm0nk] --no-execute set; stopping after plan. See {job_dir}/plan.md")
        return 0

    executor_prompt = (
        "PLAN FROM STRATEGIST:\n\n"
        f"{plan_text}\n\n"
        "Execute the plan now. Be autonomous."
    )
    rc, _ = run_role(
        role="executor",
        system=EXECUTOR_SYSTEM,
        prompt=executor_prompt,
        model=args.model,
        job_dir=job_dir,
        auto_run=True,
    )
    print(f"[kyberm0nk] done rc={rc} job={job_dir}")
    return rc


def cmd_list(_: argparse.Namespace) -> int:
    if not JOBS_DIR.exists():
        print("(no jobs)")
        return 0
    rows = []
    for meta_path in sorted(JOBS_DIR.glob("*/meta.json"), reverse=True):
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:
            continue
        rows.append((meta.get("id", "?"), meta.get("created_at", "?"),
                     meta.get("goal", "?")[:80]))
    for r in rows:
        print(f"{r[0]}  {r[1]}  {r[2]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="kyberm0nk-pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Run a goal through planner + executor")
    pr.add_argument("goal", help="Operator goal in plain language")
    pr.add_argument("--model", default=DEFAULT_MODEL)
    pr.add_argument("--no-execute", action="store_true",
                    help="Plan only; do not invoke executor")
    pr.set_defaults(func=cmd_run)

    pl = sub.add_parser("list", help="List past jobs")
    pl.set_defaults(func=cmd_list)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
