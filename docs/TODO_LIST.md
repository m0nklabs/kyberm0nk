# TODO List

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

## Phase 2 - Docker Stack

- [x] Add a minimal base image for shared agent tooling. (Opted for separate tool images)
- [x] Add a compose service for Aider.
- [x] Add a compose service for OpenCode.
- [x] Add a compose service for Agent Zero.
- [x] Add shell wrappers under `scripts/`.

## Phase 3 - Safety and Observability

- [x] Add mount validation before startup.
- [x] Add Guardian health checks.
- [x] Add per-tool logs with timestamps.
- [x] Add a status command showing active project, reference mounts, and model target.

## Phase 4 - Aider Smoke Test (The Scalpel)

- [x] Execute `scripts/aider.sh` against the KyberM0nk repo itself.
- [x] Verify Aider can read the Guardian model via `host.docker.internal:11434/v1`.
- [x] Verify Aider can successfully apply a file edit (smoke test).
  - *Note: Proved volume mount & proxy work via shell commands, but Aider's parser struggles with Qwen3's diff generation. `whole` or `udiff` formats fail to apply automatically. Requires tuning `edit-format`.*
- [x] Confirm Aider logging output has proper timestamps in `logs/aider/`.

## Phase 5 - OpenCode Integration (The General)

- [x] Bootstrap OpenCode configuration inside its Docker context.
- [x] Verify it identifies the active project (`/workspace/project`).
- [x] Evaluate OpenCode's workspace context gathering capabilities.
- [x] Update `configs/opencode` with optimized system prompts for the General role.

## Phase 6 - Agent Zero Sandbox (Special Ops)

- [x] Verify Agent Zero strict mounts (rw on active, ro on references).
- [x] Run a test script via Agent Zero to confirm execution bounds.
- [x] Restrict Agent Zero from modifying parent/host resources unexpectedly (impl. via Docker `cap_drop` and `security_opt: no-new-privileges` in compose).

## Phase 7 - Continue IDE Integration (The Glasses)

- [x] Generate standard `config.json` (or `.yaml`) payload for Continue linking to Guardian.
- [x] Place `config.yaml` in `configs/continue/` as a template for easy copying to `~/.continue/`.
- [x] Verify autocomplete model routes to local endpoint.

## Phase 8 - Guardian Context Benchmarking

- [x] Add a reusable Guardian context benchmark script.
- [x] Record GPU utilization, power, memory, request timing, and timeout status.
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
- [ ] Run a contained Claude Code / Claude Agent SDK smoke test as the premium quality baseline.
- [x] Separate Claude Code's local default model pinning from sibling app runtime model configs so repo-specific Gemma settings do not bleed into Claude runtime assumptions.
- [x] Add project-scoped Claude context guardrails: compact-preservation instructions, a live statusline warning at roughly 100k tokens, and hooks that block large whole-file reads or `@file` inlines.
- [x] Make the Claude statusline prefer Guardian-advertised context for local `claude-local` sessions instead of Claude Code's rounded `200k` provider default.
- [x] Check host prerequisites for Claude Squad and Superset evaluation.
- [x] Evaluate Claude Squad as the fastest tmux/worktree TUI spike for local agents.
- [x] Evaluate Superset as the richer multi-agent worktree cockpit.
- [x] Build the Superset Linux CLI from source and verify the command surface starts locally.
- [x] Prototype a Guardian-backed Superset custom agent preset for OpenCode or Aider.
- [x] Test Superset CLI host-server flow with a disposable local workspace after a Superset session or API key is available.
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

## Phase 10 - CrewAI Main Quest Project Manager

- [x] Fork CrewAI-Studio under `m0nklabs/CrewAI-Studio` for Kyber-specific provider improvements.
- [x] Add dedicated OpenRouter and Guardian providers to the fork so cloud and local models can coexist in one crew.
- [x] Add Kyber bootstrap/status scripts for the ignored local CrewAI-Studio checkout.
- [x] Add a main quest model policy and importable CrewAI-Studio crew seed.
- [x] Document the watchable CrewAI project-manager workflow.
- [x] Add direct CrewAI project config files and a no-token dry-run validator.
- [x] Add a DB seeder so the main quest crew can be installed without manual Import/Export UI steps.
- [x] Extend the CrewAI MCP from read-mostly project inspection into live run control hooks.
- [x] Add steering hooks to the CrewAI MCP so operator guidance can be updated without dropping to manual file or terminal flows.
- [x] Add a safe live-pilot mode for the main quest crew with explicit repo-write guardrails and better exact-file repository lookup.
- [ ] Add a true live steering panel or tool so operator chat can be injected into an active run instead of only between reruns.
- [ ] Pilot the main quest crew against a disposable game project slice.
- [x] Serialize Guardian-backed CrewAI kickoff behind Guardian idle status and surface OpenRouter credit warnings before cloud-backed live runs.
- [x] Switch the main quest's default OpenRouter route to MoniFuse top20 value-ranked models instead of premium-priced defaults.
- [x] Allow Claude to assemble or revise a CrewAI team through the CrewAI MCP while constraining all OpenRouter picks to the MoniFuse top20 value pool.
- [x] Document the Kyber operator boundary: manage agent frameworks themselves, especially Hermes, and avoid doing the framework's downstream domain work by hand.
- [x] Add direct CrewAI YAML passthrough for provider-specific LLM request options so OpenRouter GPT-5.4 can be requested with `reasoning.effort=xhigh`.
- [x] Harden the CrewAI live watcher so raw log content is escaped safely and the page hooks into new live lines without replaying stale historical errors.
