# KyberM0nk

Local agentic coding cockpit powered by Guardian.

KyberM0nk is the headless server-side control plane for a local coding-agent stack. It coordinates host-native coding frameworks and supporting extras around the existing Guardian proxy and llama.cpp backend, without owning model files or starting standalone inference servers.

Claude Code is now treated as the primary host-native operator tool on this server, with its tracked home under `/home/flip/claudecode`. Kyber remains the broader lab for local supporting workers, orchestration, and sandboxed tooling.

## Core Idea

- Claude Code stays host-native and out of Docker.
- Guardian and `llama-server` stay outside Docker.
- Active Kyber-managed frameworks run host-native under dedicated home paths, with upstream source checkouts kept on their real repo names such as `~/aider`, `~/crewAI`, `~/opencode`, `~/langgraph`, `~/superset`, and `~/agentzero`.
- Workspace-first is the guiding rule: every framework should attach to one explicit project root, even if the framework stores its own metadata elsewhere.
- Source checkouts and runtime/install paths are separate concerns: `~/crewAI`, `~/opencode`, and `~/langgraph` are upstream repos, while `~/crewai`, `~/venvs/kyber-workers`, and `~/.opencode` remain runtime/install paths. See [docs/WORKSPACE_INVENTORY.md](docs/WORKSPACE_INVENTORY.md).
- Docker is optional for mature, shareable deployment targets, not the active Kyber development layer.
- Editor-side clients such as Continue are optional operator conveniences outside the runtime path.
- Active projects are selected explicitly for host-side worker execution.
- Reference repositories stay host-visible and should remain read-only by convention unless the operator chooses otherwise.

Kyber and Hermes do not require an active editor session, editor plugin, browser UI, or desktop GUI. Runtime work is driven by CLI commands, Telegram, webhooks, cron jobs, systemd services, and persisted local state.

## Available Stack

| Role | Tool | Purpose |
|------|------|---------|
| Primary operator | Claude Code | Main goto tool for high-trust repo work, review, and orchestration entry |
| Scalpel | Aider | Host-native focused code-edit worker under `~/aider` (active default implementation lane) |
| Strategist (optional) | OpenCode | Available host-native planning/execution lane via `~/venvs/kyber-workers`; not in default queue flow unless enabled |
| Operator (optional) | Agent Zero | Available host-native operator runtime under `~/agentzero`; not in default queue flow unless enabled |
| Optional editor client | Continue | Manual inline assistance against local Guardian models; not part of daemon execution |
| Gatekeeper | Guardian | OpenAI-compatible broker for local models |
| Engine | llama.cpp | GPU inference backend managed by Guardian |

## Current End-to-End Workflow

Kyber's current production workflow is:

1. A new GitHub issue (or operator request) enters Hermes.
2. Hermes triages the issue and assigns exactly one issue at a time to the coding-agent lane.
3. Hermes persists the run in SQLite and queues it FIFO.
4. The single-flight local coder lease claims exactly one queued run.
5. The coding agent opens or reuses the PR branch and implements the issue in that PR.
6. Local validation runs before review handoff.
7. The coding agent marks the PR `ready_for_review`.
8. Tier1 reviewer checks the PR with a fast OpenRouter model.
9. If Tier1 is clean, Tier2 reviewer re-checks with a stronger OpenRouter model.
10. The reviewer posts a machine-readable `kyber-tag` block that tells the PR manager whether to run `coding_subagent`, `rerun_reviewer`, or mark the PR `ready_for_merge`.

GitHub Copilot mentions are intentionally excluded from PR and issue automation.

## Intended Default Model

The initial local deep model target remains Guardian alias `qwen3-35b-uncensored`, which currently resolves to `Qwen3.6-35B-A3B-HauhauCS-Aggressive` in Guardian.

KyberM0nk must not edit Guardian model settings automatically. Model loading, pinning, tensor split, context, and VRAM policy remain owned by `~/llama_cpp_guardian/config/models.yaml`.

Kyber's `claude-local` launcher defaults Claude Code to `qwen3-35b-uncensored` and exports Claude-side compaction tuning for the local Guardian/Qwen route, with the default threshold set to `compact@120k` instead of shrinking Guardian's runtime context. That choice is independent from per-project application configs, so a sibling app such as NerveSplat may keep `gemma4-e4b` for its own runtime without changing what Claude Code should use for coding work.

## Documentation

Start here:

- [docs/index.md](docs/index.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/GITHUB_ISSUE_RESOLUTION.md](docs/GITHUB_ISSUE_RESOLUTION.md)
- [docs/TOOL_ROLES.md](docs/TOOL_ROLES.md)
- [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md)
- [docs/WORKSPACE_POLICY.md](docs/WORKSPACE_POLICY.md)
- [docs/WORKSPACE_INVENTORY.md](docs/WORKSPACE_INVENTORY.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/kyber-tag.jsonschema](docs/kyber-tag.jsonschema)
- [docs/audit-report.md](docs/audit-report.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/LOCAL_AGENT_MODEL_SETTINGS.md](docs/LOCAL_AGENT_MODEL_SETTINGS.md)
- [docs/VALIDATION_LOG.md](docs/VALIDATION_LOG.md)
- [docs/TODO_LIST.md](docs/TODO_LIST.md)
- [docs/AGENT_HANDOFF_PROMPT.md](docs/AGENT_HANDOFF_PROMPT.md)

## Quickstart

For the current headless Kyber path:

```bash
scripts/test_quickstart.sh
scripts/crewai_status.sh
scripts/superset.sh status
scripts/validate_docs.sh
```

Expected docs validation result:

```text
docs validation: OK
```

## Superset Orchestration

Superset is the current preferred session/worktree cockpit for KyberM0nk.

- Website: https://superset.sh
- Docs: https://docs.superset.sh
- Repository: https://github.com/superset-sh/superset

Kyber entry point. Superset now runs from the host checkout at `~/superset` with local state under `~/.superset`:

```bash
scripts/superset_bootstrap.sh
scripts/superset.sh link
scripts/superset.sh login
scripts/superset.sh status
scripts/superset.sh start
scripts/superset.sh seed-agents
scripts/superset.sh import-active
```

The Superset presets route into the host-native Aider runtime at `~/aider` and the host-native OpenCode worker root at `~/venvs/kyber-workers`.

## CrewAI Main Quest Manager

Direct host-native CrewAI is the active project-manager lane for the game-development main quest. Superset remains the broader Kyber cockpit; CrewAI is the focused planning and project-manager path around the tracked NewNexus crew.

The upstream CrewAI source checkout now lives at `~/crewAI`, while the direct runnable runtime stays at `~/crewai` so the repo name can match GitHub without breaking the existing host runtime path.

```bash
scripts/crewai_bootstrap.sh
scripts/crewai_status.sh
scripts/crewai_main_quest_dry_run.sh
```

Optional live foreground run:

```bash
scripts/crewai_main_quest_run.sh
```

The tracked `scripts/crewai_main_quest_control.py` path now owns foreground runs, background runs, status, stop/restart, and persisted steering inputs. Legacy `crewai_studio_*` wrappers remain only as compatibility shims and no longer define the active Kyber path.

The shared `scripts/crewai_main_quest_control.py` path now enforces two kickoff guardrails for live runs: Guardian-backed workers wait for Guardian to go idle before they start competing for the same local GPU route, and OpenRouter-backed runs emit a credit warning before cloud spend begins. The balance check uses `GET /credits` when the configured key is a management key; otherwise Kyber still warns that cloud spend will happen, but cannot show remaining credits automatically.

See [docs/crewai/MAIN_QUEST_PROJECT_MANAGER.md](docs/crewai/MAIN_QUEST_PROJECT_MANAGER.md).

## Repository Status

This repository now acts as the tracked control plane for host-native local frameworks plus the helper scripts and docs needed to keep them manageable.
