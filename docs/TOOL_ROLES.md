# Tool Roles

KyberM0nk is not a single autonomous agent. It is a project orchestration system with a small set of specialized tools and daemon-triggered automation lanes.

## Orchestrator - Hermes

Hermes is the orchestration brain. It manages the project maturity lifecycle:

- Issue triage and prioritization
- PR governance and lane management
- Cron-driven governance loops
- Maturity tracking across projects
- Framework routing (Aider, and future frameworks)

Use it for:
- orchestrating any project through the maturity lifecycle
- managing the issue-to-PR pipeline
- running governance loops that continuously improve project quality
- cryptotrader is the active testing playground

## Execution Worker - Aider

Aider is the focused headless code-editing worker.

Host runtime: `~/aider`

Use it for:
- targeted bug fixes
- small feature implementation
- refactors with limited blast radius
- patch review and iteration

Aider should operate inside one active project mounted read-write.

### PR Review Automation Contract

For PR and issue handling lanes, Kyber does **not** use GitHub Copilot as the
review or coding executor.

Required review loop:

1. Tier1 Aider reviewer runs first (fast, lower-cost OpenRouter model).
2. If Tier1 finds issues, it posts inline findings and sets PR-manager tags for
    `coding_subagent`.
3. If Tier1 is clean, Tier2 Aider reviewer runs with a stronger OpenRouter model
    (for example `deepseek-v4-pro` with max reasoning effort when configured).
4. If Tier2 finds issues, it posts inline findings and tags the PR for
    `coding_subagent`.
5. If Tier2 is also clean, it tags the PR as `ready_for_merge`.

The PR manager must route next actions from machine-readable tags in review
comments, not from `@copilot` mentions.

## Gatekeeper - Guardian

Guardian is the OpenAI-compatible broker for local model access.

KyberM0nk should only call Guardian. It must not start or control raw `llama-server` instances.

## Engine - llama.cpp

`llama-server` is the inference backend. It is managed by Guardian and remains outside KyberM0nk.

## Optional Tools

- **OpenCode** — high-level planning and architecture. Use for multi-file project planning, feature decomposition, and architectural decisions.
- **Agent Zero** — sandboxed task runner for heavier system work. Experimental but functional.
- **Continue** — optional editor-side client for inline code suggestions and developer-in-the-loop editing. Outside the runtime path.
