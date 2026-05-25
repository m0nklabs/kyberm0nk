# KyberM0nk

Local agentic coding cockpit powered by Guardian.

KyberM0nk is the control workspace for a local coding-agent stack. It coordinates host-native coding frameworks and supporting extras around the existing Guardian proxy and llama.cpp backend, without owning model files or starting standalone inference servers.

Claude Code is now treated as the primary host-native operator tool on this server, with its tracked home under `/home/flip/claudecode`. Kyber remains the broader lab for local supporting workers, orchestration, and sandboxed tooling.

## Core Idea

- Claude Code stays host-native and out of Docker.
- Guardian and `llama-server` stay outside Docker.
- Active Kyber-managed frameworks run host-native under dedicated home paths, with upstream source checkouts kept on their real repo names such as `~/aider`, `~/crewAI`, `~/opencode`, `~/langgraph`, `~/superset`, and `~/agentzero`.
- Workspace-first is the guiding rule: every framework should attach to one explicit project workspace, analogous to a VS Code workspace, even if the framework stores its own metadata differently.
- Source checkouts and runtime/install paths are separate concerns: `~/crewAI`, `~/opencode`, and `~/langgraph` are upstream repos, while `~/crewai`, `~/venvs/kyber-workers`, and `~/.opencode` remain runtime/install paths. See [docs/WORKSPACE_INVENTORY.md](docs/WORKSPACE_INVENTORY.md).
- Docker is optional for mature, shareable deployment targets, not the active Kyber development layer.
- Continue stays in the IDE as an extension, configured against Guardian.
- Active projects are selected explicitly for host-side worker execution.
- Reference repositories stay host-visible and should remain read-only by convention unless the operator chooses otherwise.

## Current Stack

| Role | Tool | Purpose |
|------|------|---------|
| Primary operator | Claude Code | Main goto tool for high-trust repo work, review, and orchestration entry |
| Strategist | OpenCode | Host-native planning and execution worker via `~/venvs/kyber-workers` |
| Scalpel | Aider | Host-native focused code-edit worker under `~/aider` |
| Lens | Continue | IDE chat and inline assistance against local Guardian models |
| Operator | Agent Zero | Host-native operator runtime under `~/agentzero` with isolated runtime home/secrets |
| Gatekeeper | Guardian | OpenAI-compatible broker for local models |
| Engine | llama.cpp | GPU inference backend managed by Guardian |

## Intended Default Model

The initial local deep model target remains Guardian alias `qwen3-35b-uncensored`, which currently resolves to `Qwen3.6-35B-A3B-HauhauCS-Aggressive` in Guardian.

KyberM0nk must not edit Guardian model settings automatically. Model loading, pinning, tensor split, context, and VRAM policy remain owned by `~/llama_cpp_guardian/config/models.yaml`.

Kyber's `claude-local` launcher defaults Claude Code to `qwen3-35b-uncensored` and exports Claude-side compaction tuning for the local Guardian/Qwen route, with the default threshold set to `compact@120k` instead of shrinking Guardian's runtime context. That choice is independent from per-project application configs, so a sibling app such as NerveSplat may keep `gemma4-e4b` for its own runtime without changing what Claude Code should use for coding work.

## Documentation

Start here:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/TOOL_ROLES.md](docs/TOOL_ROLES.md)
- [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md)
- [docs/WORKSPACE_POLICY.md](docs/WORKSPACE_POLICY.md)
- [docs/WORKSPACE_INVENTORY.md](docs/WORKSPACE_INVENTORY.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/LOCAL_AGENT_MODEL_SETTINGS.md](docs/LOCAL_AGENT_MODEL_SETTINGS.md)
- [docs/VALIDATION_LOG.md](docs/VALIDATION_LOG.md)
- [docs/TODO_LIST.md](docs/TODO_LIST.md)
- [docs/AGENT_HANDOFF_PROMPT.md](docs/AGENT_HANDOFF_PROMPT.md)

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
