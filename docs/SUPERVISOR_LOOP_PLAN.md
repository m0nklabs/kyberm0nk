# Supervisor Loop Plan

## Purpose

The supervisor loop should reduce expensive cloud-agent usage by letting local agents do routine implementation work while a cheaper local critic watches for drift, unsafe actions, repeated failures, and review-ready output.

The goal is not to build another coding agent. KyberM0nk should stay the local cockpit and integration layer around existing tools.

## Core Decision

Use two existing layers where possible:

1. **Agent/session orchestration** for worktrees, branches, terminals, persistence, and diff review.
2. **Supervisor/critic logic** for deciding whether to continue, nudge, stop, or escalate.

KyberM0nk only owns the glue that is specific to this environment: Guardian routing, Agent Zero API control, local model budgets, Windows Unreal validation boundaries, and project-specific safety policy.

## Candidate Stack

| Candidate | Best fit | Notes |
|-----------|----------|-------|
| Superset | Main multi-agent worktree cockpit | Strong fit for parallel coding agents, worktree isolation, branch handling, and diff review. Evaluate first as the broad orchestrator layer. |
| Claude Code / Claude Agent SDK | Premium coding-agent quality baseline and optional cloud worker | Likely the strongest commercial coding-agent experience. Treat it as the benchmark for hard tasks and escalation, not as the default local Guardian-backed worker unless third-party/local routing proves reliable. |
| Claude Squad | Lightweight terminal/TUI spike | Uses tmux plus git worktrees, supports Claude Code, Codex, Aider, Gemini, and other CLI agents. Good for a fast local proof before adopting a larger desktop stack. |
| OpenHands Software Agent SDK | Possible Agent Zero replacement or second sandbox agent | Provides a Python/REST SDK, tools, workspaces, subagents, hooks, remote agent server, and an experimental critic concept. Heavier, but close to the long-term shape. |
| LangGraph supervisor pattern | Critic/supervisor brain | Good for structured handoff/state graphs. Not a session manager. Use for the decision loop only if the small MVP outgrows a simple script. |
| OpenCode and Aider | Worker agents | Keep as focused workers. OpenCode for planning/model flexibility, Aider for small file edits. |

CrewAI, AutoGen, and smolagents remain secondary research targets. They are useful general multi-agent frameworks, but they do not solve coding-agent worktree/session/diff management by themselves.

## MVP Architecture

```text
Operator / VS Code
        |
        v
Kyber Supervisor Tick
        |
        +--> Worker state: Agent Zero API, tmux/session manager, or OpenHands conversation
        +--> Repo state: git status, diff stat, selected diff, branch, dirty files
        +--> Validation state: build result, test result, Guardian status
        |
        v
Local critic via Guardian
        |
        v
Decision: continue | nudge | stop | escalate
        |
        +--> continue: no message, worker keeps going
        +--> nudge: send one to three short, kind instructions
        +--> stop: prevent unsafe edits or repeated damage
        +--> escalate: ask cloud/Copilot-level reviewer only at checkpoints
```

The first implementation should be a narrow supervisor tick, not a daemon. It should inspect one active worker context and make one bounded decision.

## Decision Schema

The critic should return strict JSON so Kyber can act without parsing prose.

```json
{
  "action": "continue",
  "confidence": 0.82,
  "message": "",
  "reason": "Worker is still progressing and has not touched unsafe files.",
  "escalation_reason": ""
}
```

Allowed actions:

| Action | Meaning |
|--------|---------|
| `continue` | Worker is on track; do not interrupt. |
| `nudge` | Send a short corrective message through the worker API. |
| `stop` | Pause the worker because it is about to do something unsafe or repeatedly destructive. |
| `escalate` | Ask a stronger cloud reviewer or human operator for a decision. |

## Escalation Policy

Cloud review is reserved for high-leverage checkpoints:

- The same edit/build task fails twice.
- The worker proposes deleting or restructuring project files outside scope.
- The worker touches protected paths, secrets, infrastructure, or Windows source paths directly.
- The build fails with an unclear architecture or dependency decision.
- A branch is ready for commit, push, or PR review.
- The local critic confidence is low on a risky decision.

Routine loops stay local.

## Safety Rules

- Keep Guardian and `llama-server` outside KyberM0nk and outside Docker images.
- Use Guardian proxy port `11434`; never call backend port `11440` directly.
- Keep Agent Zero on `gemma4-26b-agent` by default; use 31B only for explicit tuning tests.
- Worker nudges must be short and kind. Prefer one to three actionable sentences.
- Do not let workers commit, push, or create PRs without review gates.
- Do not allow direct Windows source edits for NewNexus; Linux checkout remains the source of truth.
- Every worker task should have one isolated branch/worktree when running in parallel.

## Evaluation Plan

### Local Readiness Check - 2026-05-09

The host already has the baseline tooling needed for the first framework evaluations:

| Tool | Status |
|------|--------|
| tmux | Available, version 3.4 |
| GitHub CLI | Available, version 2.45.0 |
| Go | Available, version 1.22.4 |
| Node.js | Available, version 25.6.1 |
| npm | Available, version 11.9.0 |
| Docker | Available, version 29.1.3 |

This means the Claude Squad and Superset evaluations can begin without first solving host prerequisites.

### Phase A - Session Orchestrator Evaluation

- Evaluate Claude Code as the premium quality baseline: CLI behavior, worktree/subagent isolation, permission model, MCP support, hooks, and whether Kyber can call it through Superset, Claude Squad, or the Claude Agent SDK.
- Evaluate Claude Squad as the fastest local TUI proof: tmux sessions, worktree creation, diff preview, Aider/OpenCode compatibility, Guardian environment injection.
- Evaluate Superset as the richer cockpit: multi-agent workspaces, branch isolation, review UI, CLI-agent presets, persistence, and whether it can run local Guardian-backed tools cleanly.
- Record findings in a small matrix before choosing a default orchestration layer.

Claude Code position on 2026-05-09:

- Treat Claude Code as the quality bar for agentic coding, especially for hard debugging, architecture-sensitive edits, and final review.
- Do not confuse it with the local-first Guardian stack: Claude Code is a commercial/cloud-centered agent surface, while KyberM0nk's default cost-saving loop should keep routine work on local Guardian-backed workers.
- The Claude Agent SDK is the programmable path worth evaluating if Kyber needs Claude Code's tool loop inside its own supervisor flow.
- Superset or Claude Squad can still orchestrate Claude Code as one worker among others, which is safer than making Kyber depend entirely on Anthropic auth and rate limits.

Claude Squad spike on 2026-05-09:

- Cloned into ignored local evaluation path `tmp/framework-evals/claude-squad` instead of installing system-wide.
- `go run . version` passed and reported Claude Squad `1.0.17`.
- `go test ./...` passed for the cloned evaluation copy.
- It is a strong lightweight proof for tmux plus git-worktree supervision and supports arbitrary agent programs through `--program` and profile config.
- It is TUI-first: the exposed CLI has `debug`, `reset`, `version`, and a `--program` launch flag, but no obvious headless `create/list/status/send` commands for Kyber automation.
- Config is hardcoded to `~/.claude-squad/config.json` via `os.UserHomeDir()` with no obvious XDG/config-dir override, so Kyber would need either a wrapper, upstream patch, or acceptance of global user state.
- Fit: good for manual local cockpit experiments; weaker as the programmable supervisor substrate unless extended.

Superset spike on 2026-05-09:

- Cloned into ignored local evaluation path `tmp/framework-evals/superset`.
- Installed missing prerequisites for source evaluation:
        - Bun `1.3.13` from the official `oven-sh/bun` Homebrew tap.
        - Caddy `2.11.2` from Homebrew.
        - Linux package `libxkbfile-dev` for Electron/native-keymap rebuilds.
- `bun install` passed after installing `libxkbfile-dev`.
- `bun run check:desktop-git-env` passed.
- Focused host-service agent configuration tests passed: `21 pass`, `0 fail` for `packages/host-service/src/trpc/router/settings/agent-configs.test.ts`.
- The Linux CLI binary builds from source with `bun run build:linux-x64` and starts successfully as Superset CLI `0.2.12`.
- Isolated CLI smoke with `SUPERSET_HOME_DIR` set under `tmp/framework-evals/superset` reached the expected auth gate: `status --json` returns `Not logged in` and asks for `superset auth login` or `SUPERSET_API_KEY`.
- Superset exposes a stronger automation surface than Claude Squad:
        - CLI can list/create/delete workspaces and run agents.
        - Host server can run headless on loopback and manage workspaces, ports, and agent runs.
        - MCP server exposes `workspaces_list`, `workspaces_create`, `workspaces_delete`, `agents_list`, and `agents_run`.
        - Agent configs support custom command, args, prompt transport, prompt args, and environment.
- The built-in preset list includes OpenCode, Copilot, Codex, Claude, Gemini, Cursor Agent, Amp, Pi, and custom terminal agents.
- Fit: best current candidate for the session/worktree/review layer. KyberM0nk should prefer integrating with Superset CLI/MCP/host-service before building its own parallel-agent cockpit.
- Caveat: upstream README still says macOS supported and Linux untested. The Kyber local smoke now proves the Linux CLI/host-service/workspace path works after OAuth login, but keep the integration evaluation-scoped until agent-run behavior is validated over several disposable worktrees.

Kyber integration on 2026-05-09:

- Added `scripts/superset.sh` as the local Superset entry point. The current implementation runs Superset inside `kyberm0nk-sandbox-1` from `/usr/local/superset/bin/superset` and keeps Superset state at `/root/.superset` inside the container.
- Added Superset terminal-agent wrappers for Guardian-backed OpenCode and Aider. They run from the mounted Kyber workspace and route model calls through Guardian.
- Added `scripts/seed_superset_agents.py` to idempotently add Kyber agent rows to the sandbox Superset host database after Superset auth/start has created one.
- Completed authenticated sandbox flow: the Linux distribution bundle starts `superset-host`, the Kyber repo imports through the host-service tRPC API from `/workspace/project`, and a disposable `kyber/superset-smoke` workspace/worktree is created successfully.

### Phase B - Worker SDK Evaluation

- Run a minimal OpenHands SDK hello-world against Guardian-compatible LLM settings.
- Check custom tool support, hooks, sandbox behavior, and whether its critic/subagent features reduce Kyber glue.
- Decide whether OpenHands should complement or replace Agent Zero for future sandbox work.

OpenHands SDK spike on 2026-05-09:

- Cloned the standalone SDK source into ignored local evaluation path `tmp/framework-evals/software-agent-sdk` after the main OpenHands monorepo proved to consume the SDK as a dependency rather than vendoring its source.
- The SDK workspace contains `openhands-sdk`, `openhands-tools`, `openhands-workspace`, and `openhands-agent-server`, which matches the shape Kyber needs for local workers plus optional remote sandboxes.
- The SDK `LLM` class routes through LiteLLM and accepts `model`, `api_key`, and `base_url`; Guardian works with `model="openai/gemma4-26b-agent"`, `base_url="http://127.0.0.1:11434/v1"`, and the local `KYBERM0NK_GUARDIAN_API_KEY` loaded from `.env`.
- Focused LLM smoke passed through Guardian: `LLM.completion(...)` returned `SDK_OK`.
- Standalone local agent smoke passed in a disposable scratch workspace under `tmp/framework-evals/openhands-sdk-smoke`: the OpenHands agent created `MARKER.txt` with exact content `SDK_CONVERSATION_OK` using the `file_editor` tool.
- Non-native tool-calling works against the local Gemma4 route, but the first agent attempt emitted a malformed terminal call missing `command`; the SDK fed the validation error back and the agent recovered on the next iterations. This is usable, but it confirms Kyber still needs supervisor checks around tool-call quality and repeated malformed actions.
- The SDK supports local workspaces, a remote agent server, hooks, subagents, tool presets, and conversation persistence. It is a stronger programmable worker substrate than Agent Zero for code-centric loops.
- Fit: add OpenHands SDK as a second worker path for Kyber-controlled local coding tasks. Do not replace Agent Zero yet; Agent Zero remains valuable for the already-provisioned sandbox/operator workflows, NewNexus context, and Windows validation access until OpenHands remote sandbox behavior is proven.

### Phase C - Supervisor Tick MVP

- Add a small Kyber script that reads one worker context, repo status, selected diff, and validation output.
- Ask a local Guardian critic for a structured decision.
- Send a short nudge only when the action is `nudge`.
- Log every decision with timestamp, action, reason, and worker context id.

### Phase D - NewNexus Pilot

- Use the active Agent Zero NewNexus context as the first pilot.
- Watch for protected actions: direct Windows source edits, broad `.uproject` rewrites, commits, pushes, or model switches.
- Let Agent Zero continue when it is making harmless progress, even if the route is clumsy.
- Escalate only on repeated build failure or risky project-file changes.

Pilot observation on 2026-05-09:

- Agent Zero removed the full `VisualStudioTools` plugin block after being asked to only set `Enabled` to `false`.
- The unsafe deletion was corrected manually to preserve the plugin metadata while disabling it.
- The Windows build helper still failed because it pulls the Windows checkout before building, and the current Linux checkout changes were not committed/pushed for Windows to consume.
- Windows Git also reported credential-manager/prompt failures during `git pull`, so Windows sync credentials need a separate fix before build validation can be fully automated.
- This is a good first supervisor trigger example: risky project-file deletion should produce `stop` or `nudge`, while stale Windows sync should produce `escalate` instead of more source edits.

Operator correction on 2026-05-09:

- Dedicated NewNexus Windows wrapper commands confused the worker and should not be part of the active path.
- Agent Zero should generate direct `ssh unreal-windows` commands for Windows Git sync, PowerShell discovery, UnrealBuildTool, editor launches, and validation instead of relying on Kyber-provided build/probe helpers.

### Phase E - Framework Adoption Decision

- If Claude Squad or Superset covers worktree/session/review well, integrate instead of rebuilding it.
- If OpenHands SDK provides stronger sandbox agents than Agent Zero, add it as a second worker path.
- If the handoff logic becomes complex, move the decision loop into LangGraph supervisor pattern.

## Success Criteria

- Local agents complete routine implementation loops with fewer cloud/Copilot interventions.
- The supervisor interrupts less, but catches unsafe paths and repeated failure earlier.
- Every parallel task has branch/worktree isolation.
- Review-ready diffs are easy to inspect before commit/push.
- Cloud tokens are spent on planning, risky review, and final judgment rather than routine nudges.

## Immediate Next Steps

1. Run a contained Claude Code / Claude Agent SDK smoke test and record whether it should be a premium worker, escalation gate, or benchmark only.
2. Run a Superset agent-run smoke with `kyber-opencode` or `kyber-aider` in a disposable workspace and capture terminal/session behavior.
3. Prototype a minimal Kyber OpenHands worker wrapper that pins workspace paths, Guardian env, iteration limits, and transcript logging.
4. Add the first `supervisor_tick` script only after the session/worktree candidate is chosen.
