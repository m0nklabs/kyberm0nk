# KyberM0nk

Project orchestration and maturity system powered by Hermes and agentic frameworks.

KyberM0nk is a project orchestrator that matures repositories from their current state into production-ready projects. It uses GitHub issues and PRs as the primary coordination mechanism, with Hermes as the orchestration brain and agentic frameworks (currently Aider, expandable to others) as the execution workers.

CryptoTrader is the active Phase 2 proving ground. Kyber matures it through the same generic process the stack must eventually use for unrelated repositories.

Claude Code is now treated as the primary host-native operator tool on this server, with its tracked home under `/home/flip/claudecode`. Kyber remains the broader lab for local supporting workers, orchestration, and sandboxed tooling.

## System Hierarchy

- **KyberM0nk (the system)** orchestrates the stack, chooses the active target repo, and owns the cross-repo operating model.
- **Hermes Agent (the motor)** is the generic automation engine. Hermes must stay repository-agnostic and reusable across multiple target projects.
- **GitHub (the middle layer)** is the coordination surface for issues, branches, PRs, reviews, and merge state.
- **Target repositories (the products)** are the downstream codebases being improved. Today that is CryptoTrader; later it can be any other GitHub project.

## Current Program Phases

1. **Phase 1: Framework & Gatekeeper Stabilization** — completed/ongoing hardening of the generic Hermes review, coding, and guardrail loops.
2. **Phase 2: CryptoTrader Success Story** — current focus on making CryptoTrader fully green through the Kyber -> Hermes -> GitHub -> target-repo chain.
3. **Phase 3: Multi-Repo Scaling** — future expansion where the same generic framework is pointed at additional unrelated repositories.

## Core Idea

KyberM0nk takes a project and matures it through a structured lifecycle:

1. **Diagnose** — scan the project for gaps (code quality, test coverage, documentation, infrastructure, CI/CD).
2. **Prioritize** — rank issues by impact, create or triage GitHub issues.
3. **Execute** — assign issues to agentic frameworks (Aider today, others later) via PRs.
4. **Review** — tiered review with `kyber-tag` routing ensures quality gates.
5. **Repeat** — continuous maturity loop until the project is production-ready.

Each project goes through the same cycle. CryptoTrader is the current proving ground: Kyber matures it through all phases, and the patterns proved there must remain reusable for any project.

- Claude Code stays host-native and out of Docker.
- Guardian and `llama-server` stay outside Docker.
- Active Kyber-managed frameworks run host-native under dedicated home paths, with upstream source checkouts kept on their real repo names such as `~/aider`, `~/crewAI`, `~/opencode`, `~/langgraph`, and `~/agentzero`.
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
| Orchestrator | Hermes | Durable event bus, issue triage, PR governance, cron loops, project maturity tracking |
| Execution worker | Aider | Focused code-change worker — opens PRs, fixes issues, implements features |
| Primary operator | Claude Code | High-trust repo work, review, and orchestration entry |
| Benchmark harness | Harbor | Cross-framework evaluation of Claude Code, Hermes, Aider, and future workers |
| Strategist | OpenCode | Planning and architecture (optional, not in default lane) |
| Operator | Agent Zero | Sandbox task runner (optional, not in default lane) |
| Gatekeeper | Guardian | Local model brokering (OpenAI-compatible endpoint) |
| Engine | llama.cpp | GPU inference (managed by Guardian) |

### Framework Expandability

Aider is the active default execution worker. Other agentic frameworks can be added as execution lanes without changing the orchestration layer:

- **Hermes** stays the brain — it routes issues to whichever framework is available.
- **Aider** is the current implementation lane — focused, single-flight, Guardian-backed.
- **Future frameworks** (CrewAI, LangGraph, etc.) plug in as additional lanes. Hermes manages lane selection and load balancing.
- **Guardian** serves all frameworks — model routing is framework-agnostic.

The key insight: Kyber orchestrates *projects*, not tools. Tools are replaceable; the maturity process is not.

## Current End-to-End Workflow

Kyber's production workflow matures a project through GitHub issues and PRs. The target model is a hard autonomous branch-to-merge pipeline: operators create or approve the input issue, then Hermes owns every routine step until the issue is closed.

1. A GitHub issue is created manually, by Hermes/Kanban, or by a webhook-backed intake lane.
2. Hermes claims the highest-priority eligible issue, persists the run in SQLite, and creates a dedicated feature branch. Direct work on CryptoTrader `master`/`main` is forbidden.
3. The single-flight local coder lane implements the change on that branch and pushes it to GitHub.
4. Hermes opens a PR with a clear summary, validation evidence, linked issue, and risk notes.
5. Local validation runs before review handoff.
6. The Kyber review agent runs multi-round review: fast Tier1 first, stronger Tier2 when Tier1 is clean or risk warrants it.
7. Review comments are posted as anchored GitHub feedback plus a machine-readable `kyber-tag` block.
8. If review returns `coding_subagent`, Hermes addresses the comments on the same branch and pushes fixes.
9. If review returns `rerun_reviewer`, Hermes reruns the bounded review lane without changing routing/auth.
10. If review returns `ready_for_merge`, Hermes posts a ready-for-manual-merge PR comment and Telegram ping; Flip reviews the diff and merges manually.

Routine implementation must therefore follow: **issue intake → feature branch → PR → multi-round review → fix loop → manual merge gatekeeper notification → operator merge → issue closure → Kanban done**, with zero manual intervention until the explicit operator merge gate.

GitHub Copilot mentions are intentionally excluded from PR and issue automation.

## Project Maturity Model

Kyber drives projects through maturity stages. Each stage has quality gates:

| Stage | Description | Key Activities |
|-------|-------------|----------------|
| **Diagnose** | Understand current state | Code scan, dependency audit, CI check, documentation review |
| **Stabilize** | Fix critical issues | Bug fixes, test coverage, error handling, edge cases |
| **Structure** | Build solid foundation | Architecture cleanup, naming conventions, module boundaries |
| **Automate** | CI/CD and ops | Tests, linting, deployment, monitoring, health checks |
| **Polish** | Production-ready | Documentation, performance, security, observability |
| **Sustain** | Continuous improvement | Automated PRs, governance loops, self-healing |

Cryptotrader is currently in the **Stabilize → Structure** phase. The same process applies to any project.

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
- [docs/HARBOR_EVALS.md](docs/HARBOR_EVALS.md)
- [docs/kyber-tag.jsonschema](docs/kyber-tag.jsonschema)
- [docs/audit-report.md](docs/audit-report.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/AUTONOMY_BACKLOG.md](docs/AUTONOMY_BACKLOG.md)
- [docs/LOCAL_AGENT_MODEL_SETTINGS.md](docs/LOCAL_AGENT_MODEL_SETTINGS.md)
- [docs/VALIDATION_LOG.md](docs/VALIDATION_LOG.md)
- [docs/TODO_LIST.md](docs/TODO_LIST.md)
- [docs/AGENT_HANDOFF_PROMPT.md](docs/AGENT_HANDOFF_PROMPT.md)

## Quickstart

For the current headless Kyber path:

```bash
scripts/test_quickstart.sh
scripts/validate_docs.sh
```

Expected docs validation result:

```text
docs validation: OK
```

## Repository Status

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
