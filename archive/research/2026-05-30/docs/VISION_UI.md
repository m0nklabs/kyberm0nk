# Archived Research Note

Archived: 2026-05-30
Reason: This UI-first sandbox concept no longer matches the active host-native, headless Hermes + Aider + Guardian production path.
Disposition: Kept for historical reference only; not part of the canonical runtime architecture.

# Vision: KyberM0nk Cockpit UI

> "User thinks. OpenCode plans. Agent Zero builds. Cockpit watches."

## Why a UI

KyberM0nk started as a CLI control surface, but operating two cooperating
agents (planner + executor) blind through `docker-compose exec` is painful:

- you cannot see what the agents are doing in real time
- you cannot give them a single goal and walk away
- you cannot easily review what resources they touched
- you cannot replay or compare past runs

The Cockpit closes that gap. It is the operator's pane of glass over the
sandbox.

## Roles

```
+-------------------+         +--------------------+
|    Operator       |  goal   |     Cockpit UI     |
|  (you, with mouse)| ------> |  FastAPI + SSE     |
+-------------------+         +--------+-----------+
                                       |
                                       | spawn + stream
                                       v
                          +-----------------------------+
                          |   Sandbox Container         |
                          |                             |
                          |  +-----------------------+  |
                          |  | OpenCode (Strategist) |  |
                          |  |  - reads goal         |  |
                          |  |  - produces plan      |  |
                          |  +----------+------------+  |
                          |             |               |
                          |             v               |
                          |  +-----------------------+  |
                          |  | Agent Zero (Operator) |  |
                          |  |  - executes plan      |  |
                          |  |  - uses gh, curl,     |  |
                          |  |    playwright, fs     |  |
                          |  +-----------------------+  |
                          |                             |
                          |  +-----------------------+  |
                          |  | Aider (Scalpel)       |  |
                          |  |  - on-demand only     |  |
                          |  +-----------------------+  |
                          +-----------------------------+
```

- **Operator** sets a goal in the UI. That is the only required input.
- **OpenCode** is the Strategist: it converts the goal into a structured
  plan with concrete steps and hand-off prompts.
- **Agent Zero** is the Operator-in-the-machine: it receives the plan and
  executes it autonomously, using whatever resources are mounted in the
  sandbox (filesystem, `gh`, `curl`, search APIs, Playwright, the active
  project, the KyberM0nk repo itself).
- **Aider** stays installed but is not in the default flow. It is invoked
  by Agent Zero for surgical edits when that is the right tool.
- **Cockpit** never thinks. It only routes goals, streams output, and
  records what happened.

## What the UI Shows

1. **Goal pane** — a big textarea, a "Send" button, and a model selector.
2. **Plan pane** — OpenCode's streamed plan, rendered as Markdown.
3. **Execution pane** — Agent Zero's live log, color-coded per step.
4. **Resource pane** — what is mounted, which tokens are present, what
   network access is available. This is the audit trail for "what could
   the agents have touched".
5. **Stats pane** — sandbox CPU / RAM / disk, Guardian latency, current
   model. Updated every few seconds via Chart.js.
6. **Job history** — past goals with their plans, logs, and timestamps,
   so a run can be replayed or reviewed.

## Pipeline Lifecycle

```
goal received
   |
   v
[plan]  OpenCode runs in sandbox via `interpreter --auto_run`,
        output streamed line-by-line to UI over SSE.
   |
   v
[approve]  optional human gate. operator can edit the plan
           before it is handed to Agent Zero.
   |
   v
[execute]  Agent Zero runs in sandbox with the plan as input,
           output streamed to UI over SSE. Errors highlighted.
   |
   v
[archive]  full transcript, plan, resource snapshot, and stats
           saved to logs/jobs/<job_id>/.
```

## Hard Rules (still apply)

- The Cockpit MUST NOT replace Guardian or talk to llama-server directly.
- The Cockpit MUST NOT mount `/var/run/docker.sock` by default.
- The Cockpit MUST run inside the sandbox container, on a single port,
  bound to `127.0.0.1` so it is not exposed on the LAN.
- All agent invocations MUST flow through Guardian on `host.docker.internal:11434`.
- Resource access (GitHub token, search keys, project mount) MUST be
  visible in the Resource pane so the operator can see what the agents
  could touch.

## Non-Goals (for v1)

- No multi-user auth. Single-operator local tool.
- No remote access. localhost only.
- No model training or fine-tuning controls.
- No replacement for optional editor-side manual editing.
- No production-grade scheduler. One job at a time is enough to start.

## Success Criteria for v1

- I can open `http://127.0.0.1:8765`, paste a goal, and watch a real
  OpenCode plan appear in real time.
- I can hit "Execute" and watch Agent Zero work through the plan with
  live logs.
- I can see at a glance which tokens, mounts, and network resources the
  sandbox currently has.
- I can see CPU/RAM stats refresh while a job is running.
- I can scroll back through previous jobs and re-open their transcripts.
- All of the above works without leaving the browser.

## Future (v2+)

- Pause / resume / cancel running jobs.
- Approval gates per step instead of per plan.
- Per-job resource grants (give Agent Zero a token for *this* job only).
- Diff viewer for files Agent Zero changed in `ACTIVE_PROJECT`.
- Multi-agent fan-out: Agent Zero spawning sub-Agent-Zeros for parallel
  subtasks, each as a tab in the UI.
