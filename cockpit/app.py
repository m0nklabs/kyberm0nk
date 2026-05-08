"""KyberM0nk Cockpit — FastAPI control plane for the unified sandbox.

Runs *inside* the sandbox container. Spawns OpenCode (planner) and
Agent Zero (executor) as subprocesses, streams their output to the
browser over Server-Sent Events, records every job to /logs/jobs/.
"""
from __future__ import annotations

import asyncio
import json
import os
import shlex
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import psutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
JOBS_DIR = Path(os.environ.get("COCKPIT_JOBS_DIR", "/logs/jobs"))
JOBS_DIR.mkdir(parents=True, exist_ok=True)

GUARDIAN_BASE_URL = os.environ.get("OPENAI_API_BASE", "http://host.docker.internal:11434/v1")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "qwen3-35b-uncensored")

OPENCODE_SYSTEM = (
    "You are OpenCode, the Strategist of the KyberM0nk cockpit. "
    "You convert a single user goal into a numbered, concrete execution plan "
    "for Agent Zero. Be explicit about files, commands, and verification "
    "steps. Do not execute anything yourself. End with a 'Hand-off prompt:' "
    "section that Agent Zero will receive verbatim."
)

# ---------------------------------------------------------------------------
# Job state
# ---------------------------------------------------------------------------


@dataclass
class Job:
    id: str
    goal: str
    model: str
    created_at: str
    status: str = "pending"  # pending | planning | planned | executing | done | failed
    plan: str = ""
    execution: str = ""
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)

    def event(self, kind: str, data: str) -> dict:
        payload = {"kind": kind, "data": data, "ts": time.time()}
        self.queue.put_nowait(payload)
        return payload

    def persist(self) -> None:
        path = JOBS_DIR / self.id
        path.mkdir(parents=True, exist_ok=True)
        (path / "meta.json").write_text(
            json.dumps(
                {
                    "id": self.id,
                    "goal": self.goal,
                    "model": self.model,
                    "created_at": self.created_at,
                    "status": self.status,
                },
                indent=2,
            )
        )
        (path / "plan.md").write_text(self.plan or "")
        (path / "execution.log").write_text(self.execution or "")


JOBS: dict[str, Job] = {}


# ---------------------------------------------------------------------------
# Subprocess streaming
# ---------------------------------------------------------------------------


async def stream_command(cmd: list[str], stdin_text: str | None = None) -> AsyncIterator[str]:
    """Yield stdout/stderr lines from a subprocess as they appear."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if stdin_text is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={**os.environ},
    )
    if stdin_text is not None and proc.stdin is not None:
        proc.stdin.write(stdin_text.encode())
        proc.stdin.write(b"\n")
        await proc.stdin.drain()
        proc.stdin.close()

    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        yield line.decode(errors="replace").rstrip("\n")
    await proc.wait()
    yield f"__exit__:{proc.returncode}"


async def run_opencode(job: Job) -> str:
    """Run OpenCode (open-interpreter) and capture the streamed plan."""
    job.status = "planning"
    job.event("status", job.status)
    chunks: list[str] = []

    cmd = [
        "interpreter",
        "--model", f"openai/{job.model}",
        "--api_base", GUARDIAN_BASE_URL,
        "--auto_run",
        "--no_tts",
        "--system_message", OPENCODE_SYSTEM,
        "--disable_telemetry",
    ]
    full_prompt = (
        f"GOAL FROM OPERATOR:\n{job.goal}\n\n"
        "Produce the plan now. Do not run code. End with the hand-off prompt."
    )
    job.event("plan_log", f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    async for line in stream_command(cmd, stdin_text=full_prompt):
        if line.startswith("__exit__:"):
            code = int(line.split(":", 1)[1])
            job.event("plan_log", f"[opencode exit {code}]")
            break
        chunks.append(line)
        job.event("plan_log", line)

    job.plan = "\n".join(chunks)
    job.status = "planned"
    job.event("status", job.status)
    job.persist()
    return job.plan


async def run_agent_zero(job: Job) -> None:
    """Hand the plan to Agent Zero and stream its execution."""
    job.status = "executing"
    job.event("status", job.status)
    chunks: list[str] = []

    # Agent Zero CLI varies; we treat it as a non-interactive prompt runner.
    # If main.py is not present, fall back to interpreter as executor.
    az_main = Path("/opt/agent-zero/main.py")
    if az_main.exists():
        cmd = ["python", str(az_main)]
    else:
        cmd = [
            "interpreter",
            "--model", f"openai/{job.model}",
            "--api_base", GUARDIAN_BASE_URL,
            "--auto_run",
            "--no_tts",
            "--disable_telemetry",
            "--system_message",
            "You are Agent Zero. Execute the plan handed to you. You may use "
            "the shell, gh, curl, playwright and the filesystem under "
            "/workspace and /config. Report progress continuously.",
        ]

    handoff = (
        "PLAN FROM OPENCODE:\n\n"
        f"{job.plan}\n\n"
        "Execute the plan now. Be autonomous. Stop only when done or blocked."
    )
    job.event("exec_log", f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    async for line in stream_command(cmd, stdin_text=handoff):
        if line.startswith("__exit__:"):
            code = int(line.split(":", 1)[1])
            job.event("exec_log", f"[agent-zero exit {code}]")
            job.status = "done" if code == 0 else "failed"
            break
        chunks.append(line)
        job.event("exec_log", line)

    job.execution = "\n".join(chunks)
    job.event("status", job.status)
    job.persist()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="KyberM0nk Cockpit")


class GoalRequest(BaseModel):
    goal: str
    model: str = DEFAULT_MODEL
    auto_execute: bool = True


@app.post("/api/jobs")
async def create_job(req: GoalRequest) -> dict:
    if not req.goal.strip():
        raise HTTPException(400, "Goal is empty.")
    job = Job(
        id=uuid.uuid4().hex[:12],
        goal=req.goal.strip(),
        model=req.model,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    JOBS[job.id] = job
    job.persist()

    async def pipeline() -> None:
        try:
            await run_opencode(job)
            if req.auto_execute:
                await run_agent_zero(job)
        except Exception as exc:  # pragma: no cover
            job.status = "failed"
            job.event("error", str(exc))
            job.persist()
        finally:
            job.event("done", job.status)

    asyncio.create_task(pipeline())
    return {"job_id": job.id}


@app.post("/api/jobs/{job_id}/execute")
async def execute_job(job_id: str) -> dict:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Unknown job")
    if job.status != "planned":
        raise HTTPException(409, f"Job is {job.status}, not planned")
    asyncio.create_task(run_agent_zero(job))
    return {"ok": True}


@app.get("/api/jobs")
async def list_jobs() -> list[dict]:
    out = []
    for job in sorted(JOBS.values(), key=lambda j: j.created_at, reverse=True):
        out.append(
            {
                "id": job.id,
                "goal": job.goal[:120],
                "model": job.model,
                "status": job.status,
                "created_at": job.created_at,
            }
        )
    # Also surface jobs persisted from earlier runs.
    for meta_path in JOBS_DIR.glob("*/meta.json"):
        try:
            meta = json.loads(meta_path.read_text())
        except Exception:
            continue
        if meta["id"] in JOBS:
            continue
        out.append({**meta, "goal": meta["goal"][:120]})
    return out


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    job = JOBS.get(job_id)
    if job:
        return {
            "id": job.id,
            "goal": job.goal,
            "model": job.model,
            "status": job.status,
            "created_at": job.created_at,
            "plan": job.plan,
            "execution": job.execution,
        }
    path = JOBS_DIR / job_id
    if not path.exists():
        raise HTTPException(404, "Unknown job")
    meta = json.loads((path / "meta.json").read_text())
    plan = (path / "plan.md").read_text() if (path / "plan.md").exists() else ""
    execution = (path / "execution.log").read_text() if (path / "execution.log").exists() else ""
    return {**meta, "plan": plan, "execution": execution}


@app.get("/api/jobs/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Unknown job")

    async def gen() -> AsyncIterator[bytes]:
        # Replay current state first.
        yield _sse({"kind": "status", "data": job.status})
        if job.plan:
            yield _sse({"kind": "plan_log", "data": job.plan})
        if job.execution:
            yield _sse({"kind": "exec_log", "data": job.execution})
        while True:
            try:
                event = await asyncio.wait_for(job.queue.get(), timeout=15.0)
            except asyncio.TimeoutError:
                yield b": keepalive\n\n"
                continue
            yield _sse(event)
            if event.get("kind") == "done":
                break

    return StreamingResponse(gen(), media_type="text/event-stream")


def _sse(payload: dict) -> bytes:
    return f"data: {json.dumps(payload)}\n\n".encode()


@app.get("/api/stats")
async def stats() -> dict:
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "mem_percent": vm.percent,
        "mem_used_gb": round(vm.used / 1024**3, 2),
        "mem_total_gb": round(vm.total / 1024**3, 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / 1024**3, 2),
        "disk_total_gb": round(disk.total / 1024**3, 2),
        "load_avg": list(os.getloadavg()),
        "ts": time.time(),
    }


@app.get("/api/resources")
async def resources() -> dict:
    def has(env: str) -> bool:
        return bool(os.environ.get(env, "").strip())

    mounts = []
    for mp in ["/workspace/project", "/config/aider", "/config/opencode", "/config/agent-zero", "/logs"]:
        p = Path(mp)
        mounts.append(
            {
                "path": mp,
                "exists": p.exists(),
                "writable": os.access(mp, os.W_OK) if p.exists() else False,
            }
        )

    tools = {tool: bool(shutil.which(tool)) for tool in ["interpreter", "aider", "gh", "git", "curl", "playwright", "python"]}

    return {
        "guardian_base_url": GUARDIAN_BASE_URL,
        "default_model": DEFAULT_MODEL,
        "secrets": {
            "GITHUB_TOKEN": has("GITHUB_TOKEN"),
            "SERPER_API_KEY": has("SERPER_API_KEY"),
            "TAVILY_API_KEY": has("TAVILY_API_KEY"),
            "PERPLEXITY_API_KEY": has("PERPLEXITY_API_KEY"),
            "OPENAI_API_KEY": has("OPENAI_API_KEY"),
        },
        "mounts": mounts,
        "tools": tools,
    }


@app.get("/api/guardian")
async def guardian_check() -> dict:
    import urllib.request

    url = GUARDIAN_BASE_URL.rstrip("/") + "/models"
    started = time.time()
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return {
            "ok": True,
            "latency_ms": round((time.time() - started) * 1000, 1),
            "models": [m.get("id") for m in data.get("data", [])][:20],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html = (STATIC_DIR / "index.html").read_text()
    return HTMLResponse(html)


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
