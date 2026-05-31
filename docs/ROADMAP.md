# Roadmap & Vision: The Project Maturity Orchestrator

KyberM0nk is a project orchestration system that matures repositories from their current state into production-ready projects. It runs on bare-metal host resources, coordinates headless daemons and CLI workers, and uses GitHub issues and PRs as the primary coordination mechanism.

Cryptotrader is the active testing playground — the same process that matures cryptotrader will mature any project.

## Current Committed Stack

KyberM0nk's committed runtime stack is deliberately small. Today the project is
only built around Hermes, Aider, and Guardian. Other agentic frameworks are
candidates for evaluation, not architecture commitments.

### 1. Guardian
- **Tool**: `llama.cpp` (GGUF) via Guardian.
- **Role**: Local OpenAI-compatible inference broker and model lifecycle guard.
- **Setup**: Runs purely on the host (outside Docker). Configured to offload to GPU (`-ngl 99` for 35B models on 28GB VRAM). Uses the `qwen3-35b-uncensored` alias as the baseline.

### 2. Hermes Gateway — Orchestration Brain
- **Tool**: Hermes Gateway.
- **Role**: Durable event bus, issue triage, PR governance, cron loops, and project maturity tracking.
- **Setup**: Runs server-side and persists runtime state under `~/.hermes`.
- **Projects**: Orchestrates any project through the maturity lifecycle — cryptotrader is the active testing playground.

### 3. Aider — Execution Worker
- **Tool**: Aider.
- **Role**: Focused headless code-change worker — opens PRs, fixes issues, implements features.
- **Setup**: Driven directly or by Hermes `/issue` jobs through Guardian.
- **Lane**: Single-flight, Guardian-backed, the default implementation worker.

## Candidate Frameworks

Other agentic frameworks can be added as execution lanes without changing the orchestration layer. Hermes routes issues to whichever framework is available; Guardian serves all frameworks.

| Candidate | Evaluation question |
| --- | --- |
| OpenCode | Does it add enough planning throughput beyond Hermes + Aider to justify another runtime? |
| Agent Zero | Does it provide a safe, reliable sandbox lane for system-level tasks without creating maintenance drag? |
| CrewAI | Does a multi-role crew add value for project-management workflows after Hermes `/issue` matures? |
| Superset | Does a richer workspace/review UI become necessary for parallel agent operations? |
| LangGraph | Does the supervisor loop outgrow a simple queue/state machine? |
| Continue or other editor clients | Does optional manual inline assistance help operators without becoming a runtime dependency? |

Adoption requires an explicit decision record with evidence, validation results,
operational cost, and rollback path. Until then, candidate frameworks stay out of
the core stack narrative.

### Framework Expansion Principle

Kyber orchestrates *projects*, not tools. Aider is the current default execution worker, but the maturity process (diagnose → stabilize → structure → automate → polish → sustain) is framework-agnostic. When a new framework is added, it becomes another lane in the same pipeline — not a replacement for the existing one.

---

## Rollout Phases

### Phase 0 - Foundation (✅ DONE)
- [x] Clean repository and workspace creation.
- [x] Documentation skeleton, security rules, architectural boundaries.

### Phase 1, 2 & 3 - Active Stack Setup & Observability (✅ DONE)
- [x] Guardian host & container health checks.
- [x] Aider wrapper/runtime validation against Guardian.
- [x] Shell wrappers with safety, mount validation, and ISO 8601 logging.

### Phase 4 - Aider Smoke-Test
- Goal: Prove Aider works reliably with Guardian before adding more moving parts.
- Deliverables: Send first prompt via Aider to edit a local file. Confirm token efficiency and editing workflow against the deep model.

### Phase 5 - Candidate Framework Evaluation Gate
- Goal: Decide whether any extra framework is justified after Hermes + Aider
    have hit a real limitation.
- Deliverables: For each candidate, document the problem it solves, a bounded
    smoke test, operating cost, failure modes, and a keep/drop decision. No
    candidate gets a permanent role from roadmap language alone.

### Phase 6 - Optional Sandbox Evaluation
- Goal: Evaluate whether a separate sandbox worker is necessary.
- Deliverables: Only if a concrete need appears, test strict mount mappings,
    external script limits, and Docker socket safety. Drop this phase if Aider and
    Hermes cover the workload cleanly.

### Phase 7 - Deferred Operator Client Evaluation
- Goal: Only evaluate optional manual operator clients if the active
    Hermes/Aider/Guardian lane exposes a real usability gap.
- Deliverables: No committed runtime deliverable. Any future client must remain
    outside the headless runtime path and must not become required for CLI,
    Telegram, webhook, cron, or `/issue` execution.

### Phase 8 - E2E Orchestration & Polish
- Goal: Seamless headless issue-to-PR flow through Hermes, Aider, and Guardian.
- Deliverables: Keep the `/issue` lane understandable, observable, resumable,
  and easy to operate without requiring extra frameworks.

### Phase 8a - Fully Autonomous CryptoTrader Issue-to-Merge Pipeline
- Goal: Make CryptoTrader the proving ground for a zero-manual-intervention
  issue-to-merge pipeline.
- Target flow:
    1. GitHub issue is created manually or by Hermes/Kanban.
    2. Hermes claims the highest-priority eligible issue and creates a feature branch.
    3. Hermes/Aider implements on that branch only; direct CryptoTrader `master`/`main` work is forbidden.
    4. Hermes opens a PR with summary, validation evidence, linked issue, and risk notes.
    5. Kyber review runs multi-round review and posts anchored findings plus `kyber-tag` routing.
    6. Hermes addresses review comments on the same branch and reruns review until clean or blocked.
    7. Hermes merges the PR after `ready_for_merge`, passing checks, and no unresolved review-findings tag.
    8. Hermes closes the issue and marks the Kanban task done.
- Acceptance criteria:
    - No direct commits or uncommitted implementation drift on CryptoTrader `master`/`main`.
    - Every CryptoTrader implementation has a branch, PR, validation evidence, and review trail.
    - Review findings become concrete fix tasks or branch updates, not advisory-only comments.
    - Merge and issue closure are automated for routine low-risk changes.
    - Blockers are reported with exact missing credential, failing check, or unsafe-risk reason.

### Phase 9 - Evidence-Based Model Tuning
- Goal: Keep the active Hermes/Aider/Guardian lane close to Copilot-style
  working patterns: broad available context, targeted retrieval, bounded output,
  and staged summaries.
- Deliverables:
    - Maintain Guardian context benchmark scripts and trend reports.
    - Use decision-order benchmarks for fast ballpark tuning before exhaustive matrices.
    - Tune only active production lanes by default. Candidate-framework tuning waits until adoption is explicitly approved.
    - Avoid defaulting agent tools to maximum context plus maximum output unless an explicit deep benchmark or stress test requires it.

### Phase 10 - Supervisor Loop
- Goal: Reduce expensive cloud-agent usage by letting the active local lane do
  routine implementation work under a lightweight critic/supervisor loop.
- Direction:
    - Treat Hermes Gateway as the durable automation substrate for recurring work, webhook-driven actions, and queue-backed execution lanes.
    - Keep Aider as the active local code-change worker until evidence shows it is insufficient.
    - Evaluate extra orchestrators only after the simple Hermes state machine cannot cover the need.
    - Evaluate graph-based supervisor patterns only if the decision loop outgrows a simple structured script.
- Deliverables:
    - Keep `docs/SUPERVISOR_LOOP_PLAN.md` as the active design note.
    - Add a minimal supervisor tick that reads worker state, git state, validation state, and emits `continue`, `nudge`, `stop`, or `escalate`.
    - Reserve cloud review for repeated failures, risky diffs, architecture decisions, and pre-commit checkpoints.

### Phase 10a - Hermes Persistent Issue Resolution Lane (Production Ready / Implemented)
- Status: Production Ready / Implemented / Validated.
- Goal: Convert GitHub issues and Master Epics into a durable, queue-backed,
  headless automation lane that can survive gateway restarts and control local
  Guardian/Aider capacity.
- Implemented capabilities:
    - Hermes Gateway `/issue` command registered through the central slash-command registry.
    - GitHub `issues` webhook automation path that converts eligible payloads into `/issue` requests.
    - SQLite state database at `~/.hermes/issue_resolution.db` with `queued`, `running`, `expanded`, `completed`, and `failed` run states.
    - Strict FIFO single-flight local coder execution so only one Aider/Guardian job uses local inference capacity at a time.
    - Gateway startup resume that returns interrupted `running` rows to `queued` and restarts pending work.
    - Master Epic detection through the `master-plan` label or `# Master Project Plan` body heading.
    - Guardian-backed decomposition of Master Epics into ordered atomic tasks and automatic GitHub sub-issue creation.
    - Tiered OpenRouter reviewer path after PR creation, with `kyber-tag` routing for `coding_subagent`, `ready_for_merge`, and `rerun_reviewer`.
- Ecosystem role:
    - Hermes now acts as KyberM0nk's durable, event-driven execution bus for GitHub issue automation, while Guardian remains the local inference backend and Aider remains the active local code-change worker.
    - The lane gives Kyber a practical bridge from project-management artifacts to autonomous local implementation without requiring always-on cloud coding agents, active editors, or GUI sessions.
- Remaining hardening:
    - Add per-repo allowlists, cancellation controls, and richer retry policy.
    - Prevent duplicate sub-issue creation when a Master Plan references an already existing GitHub issue such as `#182`.
    - Add runtime fail-closed `kyber-tag` parsing in Hermes after the Kyber schema and docs validation baseline.
    - Target state documented in `docs/ISSUE_TO_MERGE_TARGET_STATE.md` with explicit state machine, routing contracts, failure handling, and runnable checklist.
