# TODO List

## 2026-05-28 Automated GitHub Issue Resolution

- [x] Add a barebones Hermes Gateway issue-resolution lane.
- [x] Add a manual `/issue` Telegram trigger for GitHub issues.
- [x] Add GitHub `issues` webhook conversion into the same `/issue` lane.
- [x] Split Aider role configuration between Guardian local coder and OpenRouter cloud reviewer.
- [x] Detect Master Epic issues via `master-plan` label or `# Master Project Plan` body heading.
- [x] Decompose Master Epics through Guardian and create referenced sub-issues.
- [x] Add persistent issue-run state with gateway startup resume.
- [x] Add strict single-flight FIFO execution for the local Aider/Guardian coder lane.
- [ ] Add duplicate suppression for crash windows between GitHub sub-issue creation and SQLite persistence.
- [ ] Add per-repo allowlists and cancellation controls.
- [ ] Expand reviewer output into multiple anchored inline comments.

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
- [x] Create local VS Code workspace file at `/home/flip/kyberm0nk.code-workspace`.
- [x] Add agent handoff prompt for the next workspace session.
- [x] Open KyberM0nk in its own VS Code workspace.

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

## Phase 7 - Continue IDE Integration (The Glasses)

- [x] Generate standard `config.json` (or `.yaml`) payload for Continue linking to Guardian.
- [x] Place `config.yaml` in `configs/continue/` as a template for easy copying to `~/.continue/`.
- [x] Verify autocomplete model routes to local endpoint.

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
