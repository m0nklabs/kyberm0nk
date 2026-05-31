# TODO List

## 2026-05-31 Kyber Claude Code Subagents

- [x] Add a read-only repo scanner Claude subagent for easy maintenance candidate discovery.
- [x] Add a docs-sync Claude subagent for focused documentation reconciliation.
- [x] Add a validation-runner Claude subagent for targeted smoke/verification commands.
- [x] Add a changelog/TODO maintainer Claude subagent for bookkeeping updates.
- [x] Add an issue/PR triage Claude subagent for concise routing decisions.
- [x] Add a general-purpose Claude subagent for broad implementation/refactor tasks.
- [x] Add a codebase-indexer Claude subagent for lightweight repository mapping updates.
- [x] Pin explicit model selection per subagent.
- [x] Remove project-level subagent model override so per-agent model pinning is used.

## 2026-05-30 Root Hygiene Cleanup

- [x] Remove obsolete root-level one-off patch/fix scripts and stale local helper leftovers.
- [x] Keep only front-door or still-documented root artifacts in the tracked repo surface.
- [x] Add ignore guards for local history and ad-hoc root scratch files.

## 2026-05-31 Fully Autonomous CryptoTrader Issue-to-Merge Pipeline

- [x] Establish the hard rule that CryptoTrader implementation work must use branch -> PR -> review -> merge, never direct `master`/`main` edits.
- [x] Recover existing CryptoTrader local working-tree drift onto a feature branch and PR for review instead of leaving it on `master`.
- [x] Add a Hermes pre-claim git guard that refuses to start CryptoTrader implementation when the workspace is on `master`/`main` or has dirty tracked/untracked implementation files.
- [x] Add a Hermes Kanban dispatch guard that leaves dirty protected CryptoTrader checkout tasks `ready`, records `managed_dispatch_guarded`, and refuses to claim/spawn them.
- [x] Add branch naming and PR body requirements to the Hermes issue execution lane: linked issue, validation evidence, risk notes, and review handoff state.
- [x] Add a PR-manager consumer for `kyber-tag.state=review_findings` + `next_action=coding_subagent` so review comments become concrete same-branch fix work.
- [x] Add a current-head pre-merge blocker so stale `ready_for_merge` tags or unresolved `review_findings` tags cannot authorize merge.
- [ ] Add automatic merge and issue closure once review returns `ready_for_merge`, required checks pass, and no unresolved review-findings tag remains.
- [x] Add GitHub issue/PR audit comments at issue claim, PR open/reuse, review requested, review findings routed to same-branch coding, review-loop circuit breaker, and review completion.
- [ ] Add Kanban task audit comments for claim, PR open, review fixed, merge, and closure transitions.
- [x] Add a periodic CryptoTrader workspace drift watchdog that reports any dirty `master`/`main` checkout as a pipeline violation.

## 2026-05-31 OpenRouter Token Efficiency Hardening

- [x] Move routine Kyber generalist and validation-runner subagents to the fast OpenRouter route to reduce token-per-minute pressure and reserve stronger models for explicit escalation.
- [x] Document review-loop guardrails for duplicate suppression, bounded fan-out, diff-size control, and capped jittered retries.
- [ ] Add runtime support in the Hermes review script for the documented `AIDER_REVIEW_MAX_RETRIES`, `AIDER_REVIEW_RETRY_*`, `AIDER_REVIEW_PARALLELISM`, and `AIDER_REVIEW_RATE_LIMIT_COOLDOWN_SECONDS` knobs if missing.
- [x] Add a compact OpenRouter preflight command that checks auth, model availability, and rate-limit headers without running a full review.

## 2026-05-31 Issue Assignment Reliability Hardening

- [x] Document the lane-selection and assignment contract for the current Aider-only implementation lane.
- [x] Align the persisted issue-run state docs around the five stored states: `queued`, `running`, `expanded`, `completed`, and `failed`.
- [x] Extend docs validation so core issue-assignment docs must keep those persisted states visible.
- [x] Add a read-only Hermes queue-health watchdog for stale `running` rows, old `queued` rows, queue depth backpressure, recent failures, and WIP-limit violations.
- [x] Integrate the Hermes queue-health watchdog with timer-driven alert/recovery output.
- [ ] Add priority and capability metadata to `issue_runs` once Hermes has more than the default Aider implementation lane.
- [x] Add a review-loop circuit breaker for repeated `review_findings` -> `coding_subagent` ping-pong.
- [x] Add runtime validation that malformed `kyber-tag` output fails closed in the Hermes review ingestion path.

## 2026-05-30 Issue-to-Merge Target State

- [x] Define explicit state machine for issue lifecycle in `ISSUE_TO_MERGE_TARGET_STATE.md`.
- [x] Specify routing contracts between sync, governor, execution, and reviewer loops.
- [x] Document failure handling and operator visibility rules.
- [x] Deliver architecture documentation with runnable checklist.
- [x] Cross-reference target state from `ARCHITECTURE.md` and `docs/index.md`.

## 2026-05-28 Automated GitHub Issue Resolution

- [x] Add a barebones Hermes Gateway issue-resolution lane.
- [x] Add a manual `/issue` Telegram trigger for GitHub issues.
- [x] Add GitHub `issues` webhook conversion into the same `/issue` lane.
- [x] Split Aider role configuration between Guardian local coder and OpenRouter cloud reviewer.
- [x] Detect Master Epic issues via `master-plan` label or `# Master Project Plan` body heading.
- [x] Decompose Master Epics through Guardian and create referenced sub-issues.
- [x] Add persistent issue-run state with gateway startup resume.
- [x] Add strict single-flight FIFO execution for the local Aider/Guardian coder lane.
- [x] Reset interrupted `running` rows to `queued` on Hermes Gateway startup.
- [x] Persist Master Epic child mappings in SQLite for operator inspection.
- [x] Reframe `/issue` documentation as a headless Hermes Gateway daemon lane rather than an editor-driven workflow.
- [x] Reframe the Kyber roadmap so only Hermes, Aider, and Guardian are committed runtime components; all other agentic frameworks are evaluation candidates.
- [x] Add duplicate suppression for crash windows between GitHub sub-issue creation and SQLite persistence, including Master Plan references to existing issues such as `#182`.
- [x] Add per-repo allowlist controls for Hermes issue automation.
- [ ] Add operator cancellation controls for queued/running issue automation.
- [ ] Expand reviewer output into multiple anchored inline comments.
- [x] Add a pre-merge blocker for unresolved `review_findings` tags by requiring current-head `ready_for_merge` before merge eligibility; explicit operator override path and audit trail remain part of automatic merge/closure hardening.

## Hermes Enhancement Backlog

- [x] Add a fail-closed kyber-tag parser mode: one bounded rerun for malformed reviewer output, then mark the review failed/escalated instead of silently treating it as clean or repeatedly spending review budget.

## 2026-05-27 MoniFuse Service Registration

- [x] Put Agent Zero Web UI under a tracked `systemd --user` unit.
- [x] Put the CrewAI live log watcher under a tracked `systemd --user` unit.
- [x] Add the new Agent Zero and CrewAI watcher services to MoniFuse's Kyber registry surface.

## 2026-05-27 Guardian Key Attribution Cleanup

- [x] Split Kyber maintenance scripts onto `KYBERM0NK_GUARDIAN_API_KEY`.
- [x] Give CrewAI, Aider, OpenCode, and Agent Zero dedicated Guardian keys.
- [x] Remove the generic `GUARDIAN_API_KEY` dependency from the tracked Kyber wrappers and templates.

## Phase 0 - Workspace Foundation

- [x] Choose project name: KyberM0nk.
- [x] Create documentation-first repository skeleton.
- [x] Create private GitHub repository under `m0nklabs`.
- [x] Push initial skeleton to GitHub.
- [x] Create optional editor workspace convenience file at `/home/flip/kyberm0nk/kyberm0nk.code-workspace`.
- [x] Add agent handoff prompt for the next workspace session.
- [x] Verify KyberM0nk can be opened from its own project root without relying on the home-directory workspace.

## Phase 1 - Tool Discovery

- [x] Add Guardian health-check script for host and Docker.
- [x] Verify the current OpenCode install path and Docker support.
- [x] Verify Aider configuration against Guardian `/v1`.
- [x] Verify Agent Zero Docker deployment and mount strategy.
- [x] Verify Continue local provider config format.

## Phase 2 - Legacy Docker Stack (retired)

- [x] Add a minimal base image for shared agent tooling. (Opted for separate tool images)
- [x] Add a compose service for Aider.
- [x] Add a compose service for OpenCode.
- [x] Add a compose service for Agent Zero.
- [x] Add shell wrappers under `scripts/`.

## Phase 2b - Host-Native Runtime Pivot

- [x] Retire Docker as the active Kyber development path for local agent frameworks.
- [x] Rehome direct CrewAI to `~/crewai`.
- [x] Rehome Aider to `~/aider` as its explicit host-native runtime root.
- [x] Rehome Superset to `~/superset` with state at `~/.superset`.
- [x] Rehome Agent Zero to `~/agentzero` with isolated runtime home and secrets.
- [x] Repoint the active NewNexus checkout from `.agent-projects/NewNexus` to `~/NewNexus`.
- [x] Document a workspace-first policy so each agentic framework maps back to one explicit project workspace.
- [x] Document which top-level workspace directories are real repos versus runtime roots or local lab/install trees.
- [x] Clone the missing upstream framework repos under their exact GitHub repo names and repoint the shared workspace file at those real checkouts.
- [x] Stop the legacy Kyber sandbox that was still holding Agent Zero port `50001`.
- [x] Finish the host worker bootstrap with Aider under `~/aider` and OpenCode under `~/venvs/kyber-workers`.

## Phase 3 - Safety and Observability

- [x] Add mount validation before startup.
- [x] Add Guardian health checks.
- [x] Add per-tool logs with timestamps.
- [x] Add a status command showing active project, reference mounts, and model target.

## Phase 4 - Aider Smoke Test (The Scalpel)

- [x] Execute `scripts/aider.sh` against the KyberM0nk repo itself.
- [ ] Verify Aider can read the Guardian model via the host-native Guardian route.
- [x] Verify Aider can successfully apply a file edit (smoke test).
  - *Note: Proved volume mount & proxy work via shell commands, but Aider's parser struggles with Qwen3's diff generation. `whole` or `udiff` formats fail to apply automatically. Requires tuning `edit-format`.*
- [x] Confirm Aider logging output has proper timestamps in `logs/aider/`.

## Phase 5 - OpenCode Integration (The General)

- [ ] Bootstrap OpenCode in the shared host worker venv.
- [ ] Verify it identifies the active project from the host path.
- [x] Evaluate OpenCode's workspace context gathering capabilities.
- [x] Update `configs/opencode` with optimized system prompts for the General role.

## Phase 6 - Agent Zero Host Runtime (Special Ops)

- [x] Bootstrap Agent Zero under `~/agentzero`.
- [x] Restore tracked projects and runtime helpers into the host runtime tree.
- [x] Validate `scripts/agent_zero_up.sh` serves health on `http://127.0.0.1:50001/api/health`.

## Phase 7 - Optional Editor Client Integration

- [x] Generate standard `config.json` (or `.yaml`) payload for Continue linking to Guardian.
- [x] Place `config.yaml` in `configs/continue/` as a template for easy copying to `~/.continue/`.
- [x] Verify optional editor autocomplete model routes to the local endpoint.

## Phase 8 - Guardian Context Benchmarking

- [x] Add a reusable Guardian context benchmark script.
- [x] Record GPU utilization, power, memory, request timing, and timeout status.

## Phase 8b - Hermes Framework Autonomy

- [x] Add a no-agent framework surface watch for the Kyber-managed agent stack.
- [x] Add a deterministic no-agent innovation feed that proposes missing framework capability classes to the strategic autonomy lane.
- [x] Add a no-agent Hermes cron health watch that only emits on baseline alert, state change, or recovery.
- [x] Add an `autonomy-governor` skill plus a scheduled framework-only review loop.
- [x] Pin the active governance loops to the lightweight cloud review route and narrow `terminal + session_search` toolsets where needed.
- [x] Add a route-level inference canary for Guardian so Kyber watches actual model-serving health, not only UI or wrapper reachability.
- [x] Add a `framework-supervisor` skill plus a scheduled runtime-friction review loop for Hermes itself.
- [x] Split Hermes governance into a strategic autonomy lane and an operational supervisor lane to reduce duplicate recommendations.
- [x] Link the two Hermes governance lanes through native cron output chaining to reduce repeated recommendations further.
- [x] Surface live Hermes governance loops inside MoniFuse so framework development signals are visible outside Telegram.
- [x] Write benchmark outputs to ignored `logs/guardian-context-benchmarks/` files.
- [x] Document smoke, ramp, Agent Zero, and full-context benchmark presets.
- [x] Add matrix benchmarking across input sizes, completion caps, task modes, and thinking modes.
- [x] Add trend rendering for benchmark CSV outputs.
- [x] Add decision-first ordering for faster ballpark tuning runs.
- [x] Use benchmark data to choose safer Agent Zero context defaults.
- [x] Apply benchmark-based OpenCode defaults.
- [x] Document local agent model settings.
- [x] Validate OpenCode and Agent Zero after applying balanced settings.
- [x] Smoke-test Agent Zero with Guardian `gemma4-agent` after Qwen-backed runs stalled.
- [ ] Add Guardian/AZ cancellation regression tests for orphaned `llama-server` requests.
- [x] Keep Agent Zero default on `gemma4-26b-agent` after the 31B route proved too slow for routine work.
- [x] Add loop-safe Agent Zero model budgets and NewNexus anti-repeat recovery rules.
- [ ] Benchmark/tune `gemma4-31b-uncensored-max-agent` separately before using it as an Agent Zero default.
- [x] Add dedicated Windows Unreal SSH executor access for Agent Zero without mounting the full host SSH directory.
- [x] Track and restore the Agent Zero `NewNexus` project metadata after Docker rebuilds.
- [x] Perform initial framework scan for supervisor-loop and parallel coding-agent orchestration candidates.

## Phase 9 - Supervisor Loop and Framework Evaluation

- [x] Document the supervisor-loop plan and framework shortlist.
- [x] Add a canonical MCP server registry under `configs/mcp/servers.yaml` for capability-based tool selection.
- [x] Promote Claude Code to a dedicated host-native repo with tracked global config and install flow.
- [ ] Reduce Kyber surfaces that still assume Claude is only an escalation path.
- [x] Separate Claude Code's local default model pinning from sibling app runtime model configs so repo-specific Gemma settings do not bleed into Claude runtime assumptions.
- [x] Add project-scoped Claude context guardrails: compact-preservation instructions, a live statusline warning at roughly 100k tokens, and hooks that block large whole-file reads or `@file` inlines.
- [x] Make the Claude statusline prefer Guardian-advertised context for local `claude-local` sessions instead of Claude Code's rounded `200k` provider default.
- [x] Check host prerequisites for Claude Squad and Superset evaluation.
- [x] Evaluate Claude Squad as the fastest tmux/worktree TUI spike for local agents.
- [x] Evaluate Superset as the richer multi-agent worktree cockpit.
- [x] Build the Superset Linux CLI from source and verify the command surface starts locally.
- [x] Prototype a Guardian-backed Superset custom agent preset for OpenCode or Aider.
- [x] Test Superset CLI host-server flow with a disposable local workspace after a Superset session or API key is available.
- [x] Repoint the sandbox Superset wrapper to the tracked local Linux bundle so the cockpit does not depend on a missing `/usr/local/superset` install.
- [x] Move the active Superset checkout to `~/superset` and default host state to `~/.superset`.
- [ ] Complete Superset login/auth on the host-native wrapper path.
- [x] Run an OpenHands Software Agent SDK smoke test against Guardian-compatible LLM settings.
- [x] Decide whether OpenHands should complement or replace Agent Zero for future sandbox work.
- [ ] Prototype a minimal Kyber OpenHands worker wrapper with pinned workspace, Guardian env, iteration limits, and transcript logging.
- [x] Add a minimal `supervisor_tick` script after the session/worktree layer is chosen.
- [ ] Pilot the supervisor loop against the Agent Zero NewNexus context.
- [ ] Add repeated-thought and repeated-command detection to the first supervisor tick.
- [ ] Teach worker wrappers and prompts to consult the MCP registry before asking for tools.
- [x] Add a registry sync check that compares live Claude MCP registrations against `configs/mcp/servers.yaml`.
- [ ] Fix or replace the Windows NewNexus sync path so validation builds can consume reviewed Linux checkout changes without interactive Git credential prompts.
- [ ] Add cloud escalation gates for repeated failures, risky diffs, and pre-commit review.
- [x] Document the Kyber operator boundary: manage agent frameworks themselves, especially Hermes, and avoid doing the framework's downstream domain work by hand.

## Phase 10 - CrewAI Main Quest Project Manager

- [x] Fork CrewAI-Studio under `m0nklabs/CrewAI-Studio` for Kyber-specific provider improvements.
- [x] Add dedicated OpenRouter and Guardian providers to the fork so cloud and local models can coexist in one crew.
- [x] Add Kyber bootstrap/status scripts for the ignored local CrewAI-Studio checkout.
- [x] Add a main quest model policy and importable CrewAI-Studio crew seed.
- [x] Document the watchable CrewAI project-manager workflow.
- [x] Add direct CrewAI project config files and a no-token dry-run validator.
- [x] Add a DB seeder so the main quest crew can be installed without manual Import/Export UI steps.
- [x] Rehome the default CrewAI-Studio checkout to `~/CrewAI-Studio` so the fork stays outside the Kyber repo tree while the Docker workflow remains unchanged.
- [x] Extend the CrewAI MCP from read-mostly project inspection into live run control hooks.
- [x] Add steering hooks to the CrewAI MCP so operator guidance can be updated without dropping to manual file or terminal flows.
- [x] Add a safe live-pilot mode for the main quest crew with explicit repo-write guardrails and better exact-file repository lookup.
- [ ] Add a true live steering panel or tool so operator chat can be injected into an active run instead of only between reruns.
- [ ] Pilot the main quest crew against a disposable game project slice.
- [x] Serialize Guardian-backed CrewAI kickoff behind Guardian idle status and surface OpenRouter credit warnings before cloud-backed live runs.
- [x] Switch the main quest's default OpenRouter route to MoniFuse top20 value-ranked models instead of premium-priced defaults.
- [x] Allow Claude to assemble or revise a CrewAI team through the CrewAI MCP while constraining all OpenRouter picks to the MoniFuse top20 value pool.
- [x] Add direct CrewAI YAML passthrough for provider-specific LLM request options so OpenRouter GPT-5.4 can be requested with `reasoning.effort=xhigh`.
- [x] Harden the CrewAI live watcher so raw log content is escaped safely and the page hooks into new live lines without replaying stale historical errors.
- [x] Retire CrewAI-Studio from the active Kyber path and restore direct host-native CrewAI as the supported main-quest lane.
- [x] Normalize CrewAI control/MCP state so legacy Studio metadata is translated to direct-runtime paths and status output.

## 2026-05-30 Daily Aider Advisor Lane

- [ ] Add a daily-gated Aider advisor wrapper on OpenRouter GPT-5.5 for hard questions.
- [ ] Surface advisor availability in Kyber status output and docs so Hermes knows the lane is scarce.
- [ ] Close the planning issue after implementation and validation.

## 2026-05-31 Claude Direct Provider Overrides (Idea)

- [x] Document a future-option design note for direct Claude provider/model overrides in Kyber docs.
- [ ] Pilot project-local `.claude/settings.local.json` overrides on one disposable workflow slice.
- [ ] Compare direct-provider mode vs `claude-local` + Guardian for cost, latency, and tool reliability.
