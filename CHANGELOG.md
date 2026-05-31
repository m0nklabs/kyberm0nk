# Changelog

## Unreleased

- Recorded the shipped Hermes review-loop circuit breaker (`m0nklabs/hermes-agent` commit `b77f4eef8`), which tracks repeated `review_findings` loops and fails closed after the bounded fix-attempt budget instead of ping-ponging indefinitely.
- Added tracked `hermes-queue-watchdog` systemd user service/timer units and `--emit on-change` watchdog output so Hermes queue alerts and recoveries can surface continuously without noisy healthy polls.
- Recorded the shipped Hermes fail-closed review tag parser (`m0nklabs/hermes-agent` commit `badab438f`), which requires valid reviewer routing tags, retries malformed output once, and then fails the run instead of treating malformed output as clean.
- Recorded the shipped Hermes pre-merge current-head blocker (`m0nklabs/hermes-agent` commit `7fc85409a`), which parses reviewer `head_ref_oid` tags and fails closed unless `ready_for_merge` matches the live PR head.
- Recorded the shipped Hermes review-findings consumer (`m0nklabs/hermes-agent` commit `02b09cbc5`), which requeues `review_findings` + `coding_subagent` outputs for same-branch coder fixes instead of treating reviewer feedback as terminal completion.
- Recorded the shipped Hermes branch/PR contract (`m0nklabs/hermes-agent` commit `d2a052a7c`), which creates repo-scoped CryptoTrader issue branches and PR bodies with linked issue/run, validation, risk, and review-handoff sections.
- Recorded the shipped Hermes Kanban managed-dispatch guard (`m0nklabs/hermes-agent` commit `8310636ab`), which refuses to claim or spawn CryptoTrader tasks on dirty protected `master`/`main` checkouts and emits `managed_dispatch_guarded` events.
- Reduced Kyber Claude subagent cloud-token pressure by moving the generalist and validation-runner lanes from scarce/pro models to `deepseek/deepseek-v4-flash`, while documenting explicit escalation back to stronger review only for high-risk or repeatedly failing work.
- Documented OpenRouter review-loop efficiency and rate-limit resilience guardrails: bounded fan-out, duplicate-repost avoidance, diff-size control before model escalation, and capped jittered retry knobs.
- Added `scripts/hermes_queue_watchdog.py`, a read-only Hermes queue-health and KPI probe for stale `running` rows, old `queued` rows, queue-depth pressure, recent failures, and single-flight WIP-limit violations, plus docs and environment threshold defaults.
- Clarified the Hermes issue-assignment lane contract: current routing is Aider-only and FIFO single-flight, Master Epics decompose through Guardian before Aider sub-issue execution, and `executing`/`reviewing` are documented as internal sub-states rather than persisted `issue_runs.status` values.
- Added issue-assignment state-machine coverage to docs validation and captured queue-health, priority/capability routing, review-loop circuit breaker, and fail-closed `kyber-tag` ingestion follow-ups in the TODO list.
- Tightened Hermes/Aider review routing docs and validation after the PR #309 failure analysis: unresolved `review_findings` now document a blocking merge gate, `kyber-tag` fingerprints require valid lowercase hex, and the Tier1 probe no longer fabricates validation evidence by default.
- Added `scripts/validate_kyber_tag_schema.py` plus stricter docs validation for `kyber-tag` schema examples.
- Added two additional general-purpose Claude Code subagents under `.claude/agents/`: `kyber-generalist` for broad implementation tasks and `kyber-codebase-indexer` for lightweight codebase mapping/index refresh.
- Added five project-scoped Claude Code subagents under `.claude/agents/` for Kyber maintenance lanes: repo scanning, docs sync, validation runs, changelog/TODO maintenance, and issue/PR triage.
- Added explicit per-subagent model selection (`deepseek/deepseek-v4-flash` or `deepseek/deepseek-v4-pro`) and removed the project-level `CLAUDE_CODE_SUBAGENT_MODEL` override so subagent-level model pinning is honored.
- Added a daily-gated Aider advisor lane on OpenRouter GPT-5.5 for hard questions, plus status/docs visibility so Hermes knows the advisor can only be used once per day.
- Added a new Kyber design note for future direct Claude provider/model overrides (`docs/CLAUDE_PROVIDER_OVERRIDES_IDEA.md`), including caveats, rollout guards, and pilot evaluation steps.

## 2026-05-30

- **Hermes issue assignment clarification:**
  - Clarified that Hermes assigns exactly one queued issue at a time to the coding-agent lane.
  - Documented that the coding agent resolves the issue in a PR, tags it `ready_for_review`, and only then enters the review loop.

- **Issue-handling workflow expansion in docs:**
  - Expanded the architecture and README workflow definitions to include explicit issue intake and triage by Hermes.
  - Documented coding-agent assignment, PR branch creation/reuse, implementation in the PR, and the `ready_for_review` handoff before the review loop.
  - Updated issue-resolution docs so review routing clearly starts after coding completion and ready-for-review tagging.

- **Root hygiene cleanup:**
  - Removed obsolete one-off patch/fix scripts and stale local history artifacts from the repository root.
  - Removed old Windows Unreal helper leftovers that were no longer referenced by the active Kyber runtime or docs.
  - Added `.gitignore` guards so deleted root clutter does not drift back into the tracked repo surface.
- **Tiered Aider PR review policy (no GH Copilot in PR/issue handling):**
  - Documented the canonical PR review loop as Tier1 Aider reviewer -> Tier2 Aider reviewer -> tag-driven PR manager routing.
  - Documented that PR/issue handling lanes must not rely on `@copilot` mentions for review or coding execution.
  - Standardized PR-manager next-step routing keys: `review_findings` -> `coding_subagent`, `review_clean` -> `ready_for_merge`, and `review_inconclusive` -> `rerun_reviewer`.
- **Documentation audit baseline:**
  - Updated README, architecture, issue-resolution docs, roadmap, and scripts docs to reflect the current Hermes + Aider + SQLite queue + tiered review workflow.
  - Added a machine-readable `kyber-tag` schema, a structured docs audit report, and explicit contributing guidance for docs PRs.
  - Archived obsolete research docs under `archive/research/2026-05-30/` instead of deleting them.
- **Documentation contract closure:**
  - Added `docs/index.md` as docs landing page and fixed workspace-path mismatches in setup/TODO docs.
  - Added machine-parseable inventory deliverables `docs/audit-inventory.csv` and `docs/audit-inventory.json`.
  - Added quickstart smoke helper `scripts/test_quickstart.sh` and extended docs validation expectations.

## 2026-05-28 - Persistent Issue Resolution Lane

### Added

- Added the first production-ready Hermes Gateway `/issue` automation lane for GitHub issue resolution.
- Added a headless, server-side event-driven execution model for `/issue` that works from CLI, Telegram, and webhook triggers without requiring an active editor or GUI session.
- Added SQLite-backed issue-run persistence at `~/.hermes/issue_resolution.db` with `issue_runs` and `master_subissues` tables.
- Added strict FIFO single-flight execution for the local Aider/Guardian coder lane.
- Added Master Epic detection via the `master-plan` label or a `# Master Project Plan` issue body heading.
- Added Guardian-backed Master Epic decomposition into ordered atomic tasks.
- Added automatic GitHub sub-issue creation with `Part of Master Issue #X` references.
- Added gateway startup resume logic that resets interrupted `running` rows back to `queued` and restarts queued work.
- Added the GitHub `issues` webhook automation route that converts webhook payloads into the same `/issue` lane while ignoring pull-request-shaped issue events.
- Added focused tests for command parsing, Aider invocation roles, Master Epic detection, decomposition parsing, SQLite FIFO state, and sub-issue expansion.

### Changed

- Changed `/issue` handling from direct background execution to persistent queue submission through `submit_issue_resolution()`.
- Changed project positioning for this lane from editor-assisted workflow to standalone Hermes Gateway daemon automation.
- Changed the Kyber roadmap to define only Hermes, Aider, and Guardian as the committed runtime stack; OpenCode, Agent Zero, CrewAI, Superset, LangGraph, and editor clients are now documented as evaluation candidates only.
- Changed local coder execution to occupy only one Guardian/Aider slot at a time, preventing parallel local VRAM contention.
- Changed issue-run completion tracking so normal and sub-issue runs store PR metadata after PR creation or discovery.
- Changed Master Epic execution to enter an intermediate `expanded` state until all child sub-issue runs complete.
- Kept the cloud reviewer path on OpenRouter using `deepseek/deepseek-v4-flash` with prompt caching and no auto-commits.

### Fixed

- Fixed restart behavior for interrupted local coder runs by restoring `running` rows to `queued` on Hermes Gateway startup.
- Fixed duplicate active submissions for the same repo and issue by reusing incomplete `queued`, `running`, or `expanded` rows.
- Fixed operational visibility by documenting SQLite inspection queries and the exact Master Epic trigger contract.
- Fixed architecture documentation that could imply an active VS Code/editor session is required for Hermes automation.

### Validation

- Focused Hermes gateway regression set passed: 121 tests passed, 0 failed.
- Validated files include the issue-resolution lane, gateway command help, webhook adapter, and command bypass behavior.

### Commits

- `12a3fdfc7 feat(gateway): add persistent issue resolution queue`
- `4670f74 docs(issue-resolution): document master epic queue`

## 2026-05-27

- **Host-managed framework services:**
  - Added tracked user-service definitions for Agent Zero Web UI and the CrewAI live log watcher so both surfaces can run under `systemd --user` instead of ad-hoc background shells.
  - Added a foreground mode to `scripts/agent_zero_up.sh` so the Agent Zero unit can supervise the real `run_ui.py` process while keeping the manual background launcher intact.
  - Added the CrewAI watcher runtime dependencies to the tracked `configs/crewai/requirements.txt` contract so future bootstrap runs install the FastAPI/Uvicorn stack needed for port `8509`.

- **Dedicated Guardian keys per Kyber framework:**
  - Split Kyber's shared Guardian credential into dedicated runtime keys for Aider, OpenCode, CrewAI, Agent Zero, and Kyber maintenance scripts.
  - Rewired the host wrappers, Docker sandbox env, CrewAI model policy, and live `.env` template away from the generic `GUARDIAN_API_KEY` variable.
  - Reserved a dedicated `langgraph-lab` Guardian key for future local LangGraph experiments so workspace attribution stays app-scoped.

## 2026-05-25

- **Hermes framework autonomy hardening:**
  - Added a new no-agent `Hermes Cron Health Watch` loop that reads the live Hermes cron registry, detects failing or overdue jobs, and only emits on baseline alert, state change, or recovery.
  - Added a local `autonomy-governor` skill plus a scheduled `Hermes Autonomy Governor` loop focused on framework-only autonomy gaps across Hermes, `~/.hermes`, and Kyber-managed framework surfaces.
  - Added a low-frequency no-agent `Guardian Inference Canary` loop that authenticates against Guardian, reads the current runtime model from `/api/status`, and probes real `/v1/chat/completions` serving health without forcing a different model alias.
  - Added a local `framework-supervisor` skill plus a scheduled `Hermes Framework Supervisor` loop focused on recurring cron failures, empty-response retries, repeated operator nudges, and missing runtime guardrails inside Hermes itself.
  - Split the two framework governance lanes more explicitly so `Hermes Autonomy Governor` now owns strategic autonomy design while `Hermes Framework Supervisor` stays on repeated runtime friction and operational hardening.
  - Added a new no-agent `Kyber Framework Innovation Feed` loop that deterministically scans the live framework control plane for missing capability classes and seeds the strategic autonomy lane with bounded innovation candidates.
  - Linked the two governance lanes through Hermes' native `context_from` output chaining so strategy and operations can see each other's last conclusion instead of echoing duplicate recommendations.
  - Wired the new innovation feeder into `Hermes Autonomy Governor` so strategic reviews now consume deterministic capability-candidate signals instead of inventing novelty from scratch.
  - Tilted the autonomy-governor lane toward capability expansion and innovative framework development so the machine keeps evolving instead of only preserving the current surface set.
  - Re-pinned the existing `CryptoTrader Goal Governor` job to the lightweight `openrouter-full` / `google/gemini-2.5-flash-lite` review route and narrow `terminal + session_search` toolsets to avoid local Guardian flake risk in governance loops.
  - Documented the operational cron limitation that `hermes cron create` still cannot set `provider`, `model`, or `enabled_toolsets`, so live governance jobs must be re-read after post-create pinning.
  - Hardened the new framework-supervisor loop to stay within `terminal + session_search` after its first live run tried the unavailable `read_file` tool.
  - Added MoniFuse visibility for live Hermes governance loops so the control plane now shows strategy, runtime-hardening, watchdog, and Guardian serving signals in one place.

- **Framework stewardship boundary:**
  - Documented the Kyber operator boundary explicitly in project instructions: Kyber sessions should manage agent frameworks themselves, especially Hermes, instead of manually doing the frameworks' downstream repo or operating work.
  - Clarified that bounded validation runs are allowed, but the steady-state goal is to push recurring work back into Hermes' own prompts, cron jobs, kanban flow, skills, and runtime policy.

- **Host-native framework pivot:**
  - Retired Docker as the active Kyber development path for local agent frameworks and repositioned Kyber as the control repo for host-native framework checkouts plus supporting extras.
  - Rehomed Aider to the explicit host-native runtime root at `~/aider`, updated the bootstrap and wrapper defaults to use that path, and refreshed the active docs to match.
  - Moved the active Superset lane to the host checkout at `~/superset` with local state in `~/.superset`, and updated the wrapper/bootstrap flow plus docs to match the new path.
  - Moved the active Agent Zero lane to `~/agentzero` with isolated runtime home/secrets, restored tracked project provisioning on the host, and stopped the legacy Docker sandbox that was still holding port `50001`.
  - Repointed the active NewNexus checkout from `kyberm0nk/.agent-projects/NewNexus` to `~/NewNexus` across the CrewAI controller, Agent Zero provisioning, runtime defaults, and active docs/templates.
  - Documented a workspace-first policy for Kyber so each agentic framework is expected to bind to one explicit project workspace, with framework-specific metadata treated as a separate concern from the real source checkout.
  - Added a workspace inventory that distinguishes real Git checkouts from runtime roots, local install trees, and lab directories so Kyber docs stop implying every top-level path is a cloned upstream repo.
  - Converted `~/aider` from a venv-only runtime into a real upstream checkout while preserving its `.venv`, cloned upstream repos at `~/opencode`, `~/langgraph`, and `~/crewAI`, and rewired the shared multi-root workspace away from `~/.opencode`, `~/langgraph-lab`, and runtime-only `~/crewai`.
  - Hardened `scripts/agent_zero_up.sh` so it can clear stale root-owned listeners on `50001` via `sudo -n fuser` before relaunch.
  - Updated the host worker bootstrap and Agent Zero bootstrap away from the old `httpx<0.28` downgrade path, made the worker bootstrap prefer Python 3.11, split Aider/OpenCode into isolated sub-venvs under `~/venvs/kyber-workers` to avoid dependency conflicts, and pinned the OpenCode venv to `setuptools<81` so the current OpenInterpreter build still gets `pkg_resources`.
  - Refreshed the root README, workspace setup docs, environment template, and Superset/Agent Zero config docs so they describe the current host-native operating model.

- **Superset cockpit recovery:**
  - Repointed `scripts/superset.sh` from the missing `/usr/local/superset` path to the tracked local Linux bundle under `tmp/framework-evals/superset/packages/cli/dist/superset-linux-x64/bin/superset`.
  - Added an explicit sandbox-side binary check so the wrapper now fails with a precise bundle-missing message instead of an opaque OCI exec error.
  - Updated the active Superset integration docs to match the tracked bundle-based wrapper path.

- **Direct CrewAI comeback:**
  - Retired CrewAI-Studio from the active Kyber path and restored host-native direct CrewAI as the supported main-quest runtime alongside the Superset cockpit.
  - Added a direct bootstrap/runtime flow around `.venv/crewai`, including supported-Python selection for CrewAI 1.5.0 on hosts where `python3` is already 3.14.
  - Fixed direct dry-run/provider construction so Guardian and OpenRouter are routed through CrewAI's native OpenAI-compatible path instead of falling back to unavailable LiteLLM.
  - Normalized persisted controller state and Claude MCP status output so old Studio/container metadata is migrated to direct host-runtime paths.
  - Updated active operator docs and `.env.example` to describe direct CrewAI plus the Superset cockpit instead of the old Studio workflow.
  - Moved the active direct runtime default from `kyberm0nk/.venv/crewai` to `~/crewai` so CrewAI now lives at the requested host path outside Docker and outside the Kyber repo tree.

- **CrewAI-Studio host checkout rehome:**
  - Changed Kyber's default `CREWAI_STUDIO_DIR` from `kyberm0nk/.agent-projects/CrewAI-Studio` to `~/CrewAI-Studio` so the fork checkout lives outside the Kyber repo tree while staying host-local.
  - Updated the CrewAI bootstrap, status, seed, dry-run, live-run, controller, and MCP helper paths to resolve the new default location while keeping the explicit `CREWAI_STUDIO_DIR` override.
  - Refreshed the README, CrewAI docs, `.env.example`, and helper patch scripts so manual imports and local tooling point at `~/CrewAI-Studio` instead of the old `.agent-projects` path.

## 2026-05-22

- **ClaudeCode ownership split:**
  - Added the dedicated `~/claudecode/` host-native repo as the tracked home for the live `~/.claude` payload and `claude-local` launcher.
  - Repositioned Kyber docs so Claude Code is described as the primary operator lane on this server instead of a Docker-adjacent or escalation-only side path.
  - Fixed the shared Claude statusline fallback so empty smoke-test payloads no longer report a false red `COMPACT SOON` state.

- **VibeUE Claude bridge hardening:**
  - Updated `scripts/claude_mcp_vibeue.sh` to reuse an already healthy local bridge before trying to rebuild the SSH tunnel, so an existing good MCP forward no longer fails just because the port is occupied.
  - Broadened stale tunnel cleanup so old `0.0.0.0:56701` SSH forwards are actually recycled instead of surviving the wrapper's `pkill` pattern.
  - Added an explicit Windows-side hint when no interactive user session exists, because VibeUE cannot come back until a live Unreal/editor session is available.
  - Added exit-time tunnel cleanup so Claude-side MCP health checks do not leave orphaned local SSH forwards behind when the wrapper is terminated early.
  - Stopped `exec`-replacing the wrapper with `mcp-remote` so successful Claude MCP health checks also return through the shell and trigger the EXIT cleanup path.

- **Claude MCP ownership cleanup:**
  - Moved the host-level Claude MCP bridge ownership for `vibeue` and the legacy GitHub PAT wrapper into `~/claudecode/scripts/`.
  - Left compatibility shims in `kyberm0nk/scripts/` so older registrations or docs do not break during the transition.
  - Updated the Kyber MCP registry to point at the new `claudecode` wrapper paths for user-scoped Claude infrastructure.
  - Marked the old GitHub PAT wrapper as fallback-only in the Kyber MCP registry because the official `plugin:github:github` route is the active live surface now.
  - Taught the registry sync checker to ignore official plugin registrations and only enforce drift for the active user-scoped Claude MCP servers tracked in the registry.
  - Refreshed the Kyber MCP registry to match the current live Claude setup by marking Playwright as plugin-managed fallback and adding the active `modelcontextprotocol-servers-fetch`, `-git`, `-memory`, and `-sequentialthinking` registrations.

## 2026-05-19

- **VibeUE GitHub Copilot bridge:**
  - Validated the live Windows VibeUE MCP endpoint through a Linux-side SSH forward published on `http://192.168.1.35:56701/mcp`, with the same tunnel still reachable locally at `http://127.0.0.1:56701/mcp`.
  - Updated the Kyber MCP registry so the tracked `vibeue` bridge is no longer treated as Claude-only; GitHub Copilot is now an explicit supported client surface for the same Unreal-side tunnel pattern.

## 2026-05-18

- **Claude auto-compact threshold correction:**
  - Lowered the `claude-local` launcher default to a true `compact@120k` target by setting `CLAUDE_CODE_AUTO_COMPACT_WINDOW=120000` and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=100`.
  - Kept Guardian's runtime context at `131072`; the fix stays on the Claude side so a normal turn still has headroom before the provider limit is hit.

## 2026-05-17

- **Claude-side auto-compact tuning:**
  - Switched the local `claude-local` launcher to use documented Claude Code environment variables for compaction behavior on the Guardian-backed Qwen route instead of lowering Guardian's own runtime context.
  - Set launcher defaults for `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, and `CLAUDE_CODE_MAX_OUTPUT_TOKENS`, and intentionally left `CLAUDE_CODE_MAX_CONTEXT_TOKENS` unset because the docs say it only takes effect when compaction is disabled.
  - Updated both global and project Claude status lines to display the real Claude-side `compact@...` threshold derived from those environment variables instead of the earlier fixed `warn@100k` heuristic.

- **Claude launcher default correction:**
  - Reverted the short-lived lower-context Claude-specific Guardian alias experiment and restored `~/.local/bin/claude-local` to the normal `qwen3-35b-uncensored` default.
  - Kept Claude-side guardrails such as statusline and hooks, but stopped using a reduced Guardian runtime window as a fake early-compaction mechanism.

## 2026-05-16

- **Claude context guardrails:**
  - Added a project-scoped `.claude/settings.json` so Kyber Claude sessions now load a custom status line showing live context pressure, remaining tokens, and a `warn@100k` threshold instead of waiting to discover an overfull context after the fact.
  - Updated the custom status line to prefer Guardian's advertised context window for local `claude-local` sessions when Claude Code reports a rounded `200k` provider default, so local Qwen runs show the real usable window instead of an inflated budget.
  - Added `.claude/hooks/guard_large_read.py` and `.claude/hooks/block_large_mentions.py` plus shared sizing helpers so oversized whole-file `Read` calls and large local `@file` inlines are blocked before they can waste context; the deny reason tells Claude to switch to Grep or Glob plus roughly 200-line slices.
  - Extended `CLAUDE.md` with explicit context-discipline and compact-preservation rules so compaction keeps the current goal, validation state, blockers, and live operational facts instead of collapsing them into vague summaries.

- **CrewAI live watcher hardening:**
  - Reworked `scripts/crewai_web_watcher.py` so the browser renders streamed log lines through DOM text nodes instead of raw `innerHTML`; raw log content such as `</think>` and C++ template syntax like `CreateDefaultSubobject<...>` no longer breaks the page.
  - Switched the watcher from `tail -n 150 -f` to `tail -n 0 -F` so the screen attaches to new live lines only and does not front-load stale historical errors every time it opens.

- **CrewAI MoniFuse top20 value routing:**
  - Replaced the main quest's default premium OpenRouter picks with MoniFuse value-ranked models: `deepseek/deepseek-v4-flash` for manager orchestration, `z-ai/glm-4.7-flash` for planning, `z-ai/glm-5.1` for QA review, and `deepseek/deepseek-v4-pro` only for narrow escalation.
  - Expanded the allowed OpenRouter pool from the MoniFuse top10 to a curated MoniFuse top20 route set so Claude can reach additional high-value models such as `openai/gpt-5.4`, `anthropic/claude-sonnet-4.6`, and `moonshotai/kimi-k2-thinking` without leaving the value guardrails.
  - Updated `CLAUDE.md`, `configs/crewai/model_policy.yaml`, and the main quest docs so Claude is explicitly told to stay inside the MoniFuse top20 value set for CrewAI cloud roles unless the operator asks for a premium override.
  - Added runtime `llm_kwargs` passthrough support to `configs/crewai/main_quest_project/crew.py` so direct CrewAI YAML runs can forward provider-specific OpenRouter request options such as `extra_body.reasoning.effort`.
  - Documented `openai/gpt-5.4` as an OpenRouter reasoning route that should be requested with `reasoning.effort=xhigh` when Claude picks it for a hard blocker.

- **CrewAI local-GPU serialization + cloud-credit warnings:**
  - Extended `scripts/crewai_main_quest_control.py` to inspect each CrewAI project's LLM providers before kickoff, wait for Guardian `/api/status` to go idle before starting Guardian-backed live runs, and persist the resulting `guardian_local_policy` in run state.
  - Added best-effort OpenRouter credit warnings to the same control path: live runs now announce cloud spend up front and query `GET /credits` when the configured key is a management key, falling back to an explicit "cloud spend without balance visibility" warning when only a normal key is available.
  - Enriched the control-script status payload with `llm_usage`, `guardian_local_policy`, and `openrouter_credit_policy` so Claude/MCP tools can explain why a run is waiting or when OpenRouter credits need topping up.
  - Updated `CLAUDE.md`, the root README, and the direct main-quest README so Claude is explicitly told to finish local Guardian GPU work before starting Guardian-backed CrewAI workers and to warn the operator when OpenRouter cloud spend is about to happen.

## 2026-05-15

- **Claude VibeUE bridge recovery:**
  - Reworked `scripts/claude_mcp_vibeue.sh` to probe the known Windows-side VibeUE MCP ports (`56701`, `56700`, `62352`, `62351`) and tunnel the first healthy endpoint instead of hardcoding the dead `62351` default.
  - Updated the MCP registry entry to the real Windows SSH user `ue_agent` and documented the fallback VibeUE ports so the registry matches the current multi-project Unreal setup.

- **Claude runtime/app-model separation:**
  - Updated the local `claude-local` launcher to default Claude Code to Guardian alias `qwen3-35b-uncensored`, while still allowing an explicit `--model` flag or `CLAUDE_MODEL` environment override.
  - Added a Kyber `CLAUDE.md` instruction layer and README/TODO notes clarifying that sibling app configs such as NerveSplat's `gemma4-e4b` are application-runtime settings, not Claude Code runtime settings.

- **Claude multi-project access defaults:**
  - Expanded the local `claude` and `claude-local` launchers to add all active sibling project roots (`github-copilot-config`, `kyberm0nk`, `llama_cpp_guardian`, `monifuse`, `NewNexus`, and `nervesplat`) instead of only one extra directory.
  - Added `CLAUDE_EXTRA_DIRS` support so extra project roots can be injected as a colon-separated list without editing the wrapper again.

- **Claude auto-proceed defaults:**
  - Updated the local `claude-local` launcher to default to `--permission-mode bypassPermissions`, while still allowing an explicit permission override when one is passed on the command line.
  - Updated the Kyber Superset Claude preset seed from `acceptEdits` to `bypassPermissions` so Claude sessions launched through that cockpit path stop asking to proceed on each action.

## 2026-05-14

- **Windows Unreal SSH identity alignment:**
  - Updated Kyber's Windows Unreal SSH defaults and sandbox SSH config to use the `ue_agent` account instead of stale `mark1`/`onyou` assumptions for headless access.
  - Updated `scripts/claude_mcp_vibeue.sh` so Claude/VibeUE tunnel setup now defaults to `ue_agent@192.168.1.245`.
  - Updated the Windows Unreal executor and headless pipeline docs to explicitly distinguish the SSH user (`ue_agent`) from the desktop/Epic Launcher user (`onyou`).

- **CrewAI MCP read-mostly v1:**
  - Extended `docker/Claude-CrewAI-MCP/crewai_mcp_server.py` from a guidance-only rulebook into a Kyber project-aware MCP surface.
  - Added project inspection, dry-run execution, CrewAI-Studio container status, and live-log preview tools so Claude can interrogate `configs/crewai/main_quest_project/` and the existing run scripts directly.
  - Updated the MCP registry and CrewAI main quest documentation to reflect that the `crewai` server is now read-mostly operational tooling, not only static rules.
  - Hardened the vendored FastMCP tester to use the MCP virtualenv interpreter and small tool-specific smoke arguments, and fixed dry-run timeout handling so the MCP returns structured timeout responses instead of crashing on partial subprocess output.

- **CrewAI MCP live-run control:**
  - Added `scripts/crewai_main_quest_control.py` as the shared control path for tracked CrewAI main-quest runs, with `run`, `start`, `status`, and `stop` modes plus persisted PID/state under `logs/crewai_state/`.
  - Updated `scripts/crewai_main_quest_run.sh` to delegate to the control script and accept environment overrides instead of hardcoding a one-off Docker exec path.
  - Extended the vendored CrewAI MCP with `start_kyber_crewai_live_run` and `stop_kyber_crewai_live_run`, and enriched `get_kyber_crewai_run_status` with control-script state so Claude can manage the tracked background run directly.
  - Validated the control script with foreground and background dry-run execution, then validated the MCP live-run control path end-to-end in `dry_run` mode.

- **CrewAI steering hooks between runs:**
  - Extended `scripts/crewai_main_quest_control.py` with persisted operator-input handling so `run` and `start` resolve inputs from saved state plus explicit overrides, and added `get-inputs`, `set-inputs`, and `restart` commands.
  - Extended the vendored CrewAI MCP with `get_kyber_crewai_operator_inputs`, `update_kyber_crewai_operator_inputs`, and `restart_kyber_crewai_live_run` so operator guidance can be updated and applied without manual file edits or terminal-only workflows.
  - Hardened the vendored FastMCP tester to skip disruptive mutation tools during the generic smoke test while still validating the safe read and status surface.
  - Validated the new steering path end-to-end: MCP guidance update, dry-run restart, status readback, restoration to the default guidance, and clean stop all completed successfully.

- **CrewAI safe live-pilot guardrails:**
  - Extended `scripts/crewai_main_quest_control.py` and `configs/crewai/main_quest_project/crew.py` with persisted `repo_write_mode` and `github_target_branch` inputs so live pilots can run in explicit no-write mode instead of blindly pushing to `m0nklabs/NewNexus`.
  - Updated the main quest task graph so `draft_implementation` produces an exact patch plan and validation checklist when repository writes are disabled, instead of pretending a push happened.
  - Extended the vendored CrewAI MCP start/restart/input-update tools to carry the same write-mode and target-branch inputs through the shared control path.
  - Fixed the direct GitHub search tool for path-style queries by attempting an exact repository file fetch before generic code search; a bounded live rerun confirmed that `filename:.uproject` now resolves to the real `NewNexus.uproject` with the expected UE 5.7 metadata instead of a documentation mention.

- **MCP sync check + supervisor tick MVP:**
  - Added `scripts/check_mcp_registry_sync.py` to compare live Claude MCP registrations against `configs/mcp/servers.yaml`, normalize descriptive transport labels such as `stdio_bridge_to_http`, and optionally fail CI-style on drift.
  - Validated the sync checker against the current live Claude MCP set; it reports `crewai`, `github`, `playwright`, and `vibeue` in sync with no missing registrations or command/arg mismatches.
  - Added `scripts/supervisor_tick.py` as the first bounded supervisor-loop artifact: it inspects one repo slice, accepts optional worker context and validation output, applies protected-path heuristics, calls Guardian for a strict JSON decision, and appends JSONL records under `logs/supervisor/`.
  - Hardened the supervisor tick for host-side execution by normalizing `host.docker.internal` Guardian URLs back to `127.0.0.1` when the Docker hostname is unavailable outside containers.
  - Validated the supervisor tick with a live Guardian critic call against the current `kyberm0nk` worktree; the script returned a `continue` decision sourced from Guardian and wrote the decision log entry locally.

- **Always-on local coding stack + MCP registry:**
  - Added `docs/CODING_MONSTER_STACK.md` to capture the current recommendation for a multi-project, local-first coding stack: Superset as orchestration layer, OpenCode/Aider as default local workers, OpenHands as programmable worker substrate, Claude Code as premium escalation, CrewAI as planning layer, and LangGraph only if the supervisor loop outgrows a small custom tick.
  - Added `configs/mcp/servers.yaml` as the canonical machine-readable MCP server registry for KyberM0nk, covering active Claude MCP servers (`crewai`, `github`, `playwright`, `vibeue`), the Superset orchestration candidate, and planned MCP gaps such as local search.
  - Updated `configs/README.md` and `docs/TODO_LIST.md` so the MCP registry becomes part of the repo structure and future worker prompts/sync checks are tracked explicitly.
  - Clarified in the stack documentation that Superset is the multi-project coding control plane candidate, while CrewAI remains the planning/project-manager layer rather than the main coding orchestrator.

- **CrewAI + Unreal helper tooling:**
  - Extended `configs/crewai/main_quest_project/` with direct GitHub search/push tools and a guarded Windows SSH execution tool so the main quest crew can inspect `m0nklabs/NewNexus`, push reviewed source changes, and trigger Windows-side Unreal validation.
  - Added local helper scripts for CrewAI live runs, web log watching, Windows SSH provisioning, local smoke testing, Claude MCP wrappers, and tracked Unreal/Python utility scripts that were previously only living in the working tree.
  - Added `docs/UNREAL_HEADLESS_PIPELINE.md` for the current Windows Unreal recovery/build checklist used by local agents.

- **Claude Code MCP + instruction layering:**
  - Added `scripts/claude_mcp_github.sh` so Claude Code can start the GitHub MCP server without storing the PAT directly in Claude config; the wrapper reads the token from the existing ignored secret file and falls back to `gh auth token` if needed.
  - Validated user-scoped Claude Code MCP connectivity for `crewai`, `github`, and `playwright`.
  - Updated `scripts/claude_mcp_vibeue.sh` to target the current VibeUE MCP server port (`62351`) and recycle stale local SSH tunnels when the MCP health check fails, so Claude Code can reconnect to the live Unreal session without manual cleanup.
  - Updated the local `claude-local` wrapper to inject GitHub token environment variables and add `github-copilot-config` as an extra Claude-accessible directory so sibling private instruction files can be imported by project `CLAUDE.md` files.

## 2026-05-13

- **NewNexus Unreal 5.7 recovery docs:**
  - Documented the VS2022 `v143` / `Win64` false-positive fix caused by Unreal using `Win64` while VS MSBuild only exposed `x64` platform targets.
  - Documented the `VisualStudioTools` plugin trap that caused Unreal's `Missing NewNexus Modules` popup and UBT `ModuleRules` failure.
  - Captured the correct NewNexus engine/project paths, SSH user vs desktop user split, and project discovery config locations for Epic Launcher and Unreal Project Browser.
  - Added manual build and validation commands for `NewNexusEditor` so future agents can verify the fix without relying on Unreal's popup rebuild path.

## 2026-05-10

- **CrewAI-Studio main quest manager:**
  - Forked `strnad/CrewAI-Studio` to `m0nklabs/CrewAI-Studio` for Kyber-specific provider improvements.
  - Added dedicated `OpenRouter` and `Guardian` providers in the fork so cloud escalation models and local Guardian models can be selected side by side in a single CrewAI-Studio crew.
  - Updated the fork's Docker Compose defaults with configurable ports and Linux `host.docker.internal` support for Guardian access from the Streamlit container.
  - Added `configs/crewai/model_policy.yaml` to encode the MoniFuse value-ranking-based model allocation for CrewAI roles.
  - Added `configs/crewai/main_quest_studio_import.json` as an importable Studio seed for the game-development project manager crew.
  - Added `scripts/crewai_studio_bootstrap.sh`, `scripts/crewai_studio_status.sh`, and `scripts/crewai_studio_seed_main_quest.sh` to keep the fork checkout ignored, runtime secrets out of Git, and the UI reproducible on port 8505.
  - Hardened the CrewAI-Studio bootstrap script to auto-select the next free port when 8505 is already allocated.
  - Isolated CrewAI-Studio Docker Compose under its own project name so it no longer inherits Kyber's main compose project when launched from the root `.env`.
  - Fixed OpenRouter key discovery for the existing `$HOME/.secrets/keys/openrouter.key` secret location.
  - Stabilized CrewAI-Studio port selection so refreshes keep the port already owned by the Studio container instead of incrementing on every restart.
  - Added direct CrewAI project config files under `configs/crewai/main_quest_project/` so the main quest crew can be built outside the Studio UI.
  - Upgraded the CrewAI-Studio seed script to install the main quest crew directly into the running Studio database.
  - Added `scripts/crewai_main_quest_dry_run.sh` to validate CrewAI object construction inside the Studio container without spending model tokens.
  - Anchored the main quest crew prompts to the NewNexus Unreal Engine project so runs do not drift into generic 2D or Unity assumptions.
  - Added a NewNexus-scoped GitHub REST search tool to the main quest crew, with `GITHUB_TOKEN` loaded from the ignored local Studio environment.
  - Added `docs/crewai/MAIN_QUEST_PROJECT_MANAGER.md` and rewrote the CrewAI brain architecture note in English around the new fork-backed workflow.

## 2026-05-09

- **Supervisor loop planning:**
  - Added `docs/SUPERVISOR_LOOP_PLAN.md` to define the local worker plus critic loop for reducing cloud-agent token usage.
  - Captured the initial framework shortlist: Superset, Claude Squad, OpenHands Software Agent SDK, LangGraph supervisor patterns, OpenCode, and Aider.
  - Added Claude Code / Claude Agent SDK as the premium coding-agent quality baseline and optional cloud-worker evaluation path, while keeping Agent Zero scoped to sandbox/operator work rather than primary coding.
  - Recorded host readiness for the first Claude Squad and Superset evaluations.
  - Captured the first NewNexus pilot observation: Agent Zero over-edited the `VisualStudioTools` plugin block, manual correction restored metadata with `Enabled: false`, and Windows build validation is now blocked by the Git sync/credential path.
  - Completed a local Claude Squad spike from an ignored evaluation checkout: version and Go tests pass, but the tool is TUI-first and lacks an obvious headless automation surface for Kyber supervisor control.
  - Completed a local Superset source spike from an ignored evaluation checkout: Bun/Caddy prerequisites installed, dependency install and desktop Git environment check pass, focused agent-config tests pass, and Superset's CLI/MCP/host-service surface is the preferred orchestration candidate.
  - Built the Superset Linux CLI from source and verified it starts locally; full host-server/workspace smoke is gated by Superset authentication or an API key.
  - Added a Kyber Superset wrapper, Guardian-backed OpenCode/Aider Superset agent wrappers, and an idempotent local Superset host-DB seeder for Kyber agent rows.
  - Validated Superset wrapper links/binary resolution, wrapper no-prompt guards, and isolated host-DB agent seeding; live host/workspace smoke remains blocked by Superset auth/API key.
  - Completed Superset OAuth login and built the full Linux distribution bundle so the CLI can start its sibling `superset-host` launcher.
  - Updated the Kyber Superset wrapper to resolve the bundled `bin/superset` layout and import the active project through the local Superset host-service tRPC API because this CLI build does not expose `projects create`.
  - Completed the live Superset flow: host daemon healthy, Kyber agents seeded, `/home/flip/kyberm0nk` imported as a project, and disposable branch/worktree `kyber/superset-smoke` created successfully.
  - Completed a local OpenHands Software Agent SDK spike from an ignored checkout: LiteLLM routes to Guardian with `openai/gemma4-26b-agent`, direct completion returned `SDK_OK`, and a disposable local agent workspace created `MARKER.txt` with `SDK_CONVERSATION_OK`.
  - Recorded the OpenHands decision: use it as a second programmable coding-worker path, not a full Agent Zero replacement yet, because remote sandbox behavior and tool-call reliability still need supervisor validation.
  - Cleaned the sandbox image setup so Bun and Claude Code are installed once for Superset/Claude evaluation instead of being repeated across unrelated Python dependency layers.
  - Reconciled Superset documentation and environment notes with the current Docker-sandbox wrapper path: `/usr/local/superset/bin/superset` plus `/root/.superset` inside `kyberm0nk-sandbox-1`.
  - Added roadmap and TODO entries for evaluating session/worktree orchestration before building custom KyberM0nk glue.

- **Tracked Agent Zero NewNexus project:**
  - Added a durable `NewNexus` Agent Zero project template under `configs/agent-zero/projects/newnexus` so project metadata survives Docker rebuilds.
  - Added `scripts/provision_agent_zero_projects.sh` and wired it into `scripts/agent_zero_up.sh` to restore missing project templates without recreating the sandbox.
  - Added `scripts/ensure_newnexus_checkout.sh` and ignored `.agent-projects/` so the persistent NewNexus working checkout stays local to the host and out of KyberM0nk commits.
  - Hardened project provisioning to trust the mounted NewNexus checkout for Git and remove stale runtime-only Windows helper binaries from older sandbox sessions.
  - Clarified that Agent Zero should edit `/a0/usr/projects/newnexus` and use Windows SSH for build/run validation, not as the primary source editor.
  - Added minimal `windows-pwsh` and `windows-unreal-probe` sandbox helpers so Agent Zero can obey quote-loop guard instructions without editing source through the Windows checkout.
  - Installed and documented the required Windows .NET 8 runtime for UE 5.7 `UnrealBuildTool`; the next observed build blocker is the optional `VisualStudioTools` plugin reference in `NewNexus.uproject`.
  - Added live Agent Zero GitHub credential provisioning so NewNexus commits can be pushed from the sandbox instead of routing GitHub work through the Windows Unreal workstation.
  - Added a `newnexus-windows-build` helper and hardened `windows-pwsh` to block brittle source edits through the Windows checkout.
  - Tested Guardian's max-reasoning `gemma4-31b-uncensored-max-agent` profile based on `TrevorJS/gemma-4-31B-it-uncensored`, then restored Agent Zero to the stable `gemma4-26b-agent` route after 31B proved too slow for default work.
  - Documented the Agent Zero project restore flow in `docs/AGENT_ZERO_PROJECTS.md`.
  - Removed the NewNexus-specific Windows wrapper commands from active project instructions after they proved confusing for Agent Zero; NewNexus validation now expects the worker to generate direct `ssh unreal-windows` PowerShell, Git, and UnrealBuildTool commands from known paths.
  - Reintroduced the old NewNexus Windows command names as deprecated compatibility stubs that exit with a clear message and direct workers to generate `ssh unreal-windows` commands instead of hiding the workflow behind wrappers.
  - Tightened Agent Zero's routine model budget and added NewNexus loop-recovery rules after a live run repeated the same missing-command thought instead of changing actions.
  - Added `scripts/agent_zero_unstick.sh` to stop a stuck Agent Zero UI run, reprovision tracked config, and restart with fresh runtime state.
  - Strengthened NewNexus Agent Zero instructions with action-effectiveness rules so the worker must compare state deltas, stop repeating valid-but-useless actions, and report blockers instead of compensating with unrelated edits.
  - Clarified and silenced the Agent Zero GitHub credential dry-run check so startup logs no longer look like a real `git push` updated `main`.
  - Updated Agent Zero startup to detect stale `code_execution_tool.py` file-bind mounts containing the old Windows SSH quote-loop blocker and automatically recreate the sandbox before launch.

- **Agent Zero Windows SSH diagnosis scope correction:**
  - Reverted the overbuilt Windows PowerShell helper and code-execution guard layer after the issue was confirmed to only need a clear operator-facing diagnosis.
  - Kept the Windows executor setup focused on the existing SSH alias, provisioning script, and smoke test.

- **Agent Zero Gemma4 vision route:**
  - Enabled `vision: true` for the Agent Zero `gemma4-agent` chat model route.
  - Kept Agent Zero on Guardian's bounded Gemma4 agent alias instead of switching to the full-context OpenWebUI profile.
  - Hardened `agent_zero_up.sh` so it starts an existing sandbox instead of allowing Compose to silently recreate it during config drift.
  - Removed Windows Unreal SSH key bind mounts from Compose; the dedicated key is now copied into the running sandbox by the provisioning script.
  - Added a persistent `/a0/usr/uploads` alias to Agent Zero's real `/opt/agent-zero/usr/uploads` directory so pasted clipboard images can be found by `vision_load`.
  - Patched Agent Zero's `vision_load` tool to convert local uploaded images into `data:image/...;base64,...` URLs before sending them to Guardian.

## 2026-05-08

- **Windows Unreal executor SSH access for Agent Zero:**
  - Added a dedicated sandbox SSH config for the `unreal-windows` executor alias.
  - Mounted only the dedicated Windows Unreal private key into the sandbox as a read-only secret path.
  - Documented the Windows executor security model and environment variables.
  - Added a live provisioning script that drops the Windows Unreal SSH config and key into an already-running Agent Zero sandbox without rebuilding the image or recreating the container.
  - Added a host/container smoke-test script for validating Agent Zero can execute commands on the Windows Unreal machine.

- **Agent Zero parked for primary coding-agent work:**
  - Stopped treating Agent Zero as the default interactive cockpit after repeated GPU-heavy stalls with poor progress feedback.
  - Switched the local default model alias to `qwen3-35b-reasoning-agent`, a Guardian profile with Qwen reasoning enabled but bounded.
  - Kept Agent Zero on the non-thinking alias for sandbox experiments while OpenCode/interpreter and Aider become the preferred local-agent path.

- **Agent Zero Gemma4 compatibility attempt:**
  - Temporarily switched Agent Zero chat and utility models to Guardian alias `gemma4-agent` for a bounded compatibility smoke test against the Gemma4 26B local model.

- **Agent Zero non-thinking Guardian route:**
  - Switched Agent Zero chat and utility models to Guardian alias `qwen3-35b-uncensored-agent`.
  - Added hard LiteLLM output caps in `configs/agent-zero/model_config.json` (`4096` chat tokens, `2048` utility tokens).
  - Documented why Agent Zero should use a non-thinking Qwen profile for routine tool work: Agent Zero's own installation guide warns reasoning/thinking can increase latency, and Qwen's llama.cpp guide requires a custom non-thinking chat template for the hard switch.

- **Guardian context benchmark suite:**
  - Replaced the ad-hoc 32k context test with `scripts/benchmark_guardian_context.py`.
  - Added context-size presets, JSONL/CSV output, `nvidia-smi` GPU sampling, and timeout reset protection for runaway `llama-server` requests.
  - Added a `max` preset for near-limit tests up to the current Qwen `131072` context setting.
  - Added a `reasoning-stress` task mode for comparing context prefill against long reasoning/decode behavior.
  - Added a `long-decode` task mode to force high completion-token benchmarks.
  - Expanded the benchmark into a full matrix suite across input sizes, completion caps, task modes, and thinking modes.
  - Added context budget metadata and estimated content-vs-reasoning token split columns.
  - Persist benchmark JSONL/CSV after every matrix case so long runs keep partial results if interrupted.
  - Added `--resume` support for continuing interrupted matrix runs from existing JSONL output.
  - Added `--order decision` and `--order shuffle` so runs can gather early tuning signal or spread bias instead of always walking the matrix sequentially.
  - Added `scripts/render_benchmark_trends.py` to turn benchmark CSV files into standalone trend reports.
  - Applied benchmark-based balanced defaults to Agent Zero and OpenCode.
  - Documented the local coding-agent model budget in `docs/LOCAL_AGENT_MODEL_SETTINGS.md`.
  - Added `docs/VALIDATION_LOG.md` with final validation results for the tuned OpenCode and Agent Zero settings.
  - Documented the workflow in `docs/GUARDIAN_CONTEXT_BENCHMARKS.md`.
  - Removed a hardcoded Guardian API key from `scripts/test_aider_headless.sh`.

- **Agent Zero Architecture overhaul:**
  - Removed brittle shell `sed` patching from `agent_zero_up.sh`.
  - Introduced clean, read-only volume-mounted patches (`configs/agent-zero/patches/*`).
  - Integrated a dedicated `searxng/searxng` container via `docker-compose.yml` to resolve internal localhost hardcode conflicts when Agent Zero probes for search APIs.
  - Hardened Agent Zero's heavy generation tasks by moving LLM invocation timeouts explicitly into `configs/agent-zero/model_config.json` with a generous 5-minute timeout window (`300.0s`), drastically mitigating `APITimeoutError`s during background context compaction steps with the Qwen3-35B model.

## 2026-05-06

- Initialized KyberM0nk as a documentation-first local agentic coding cockpit.
- Documented the Guardian-outside-Docker and agent-tools-inside-Docker architecture.
- Added initial role definitions, security model, workspace setup notes, and roadmap.

- Expanded `ROADMAP.md` and `TODO_LIST.md` with explicit tool hierarchy mapping (Motor, General, Executioner, Scalpel, IDE-Glasses) based on user's structural masterplan.
- Added host-level Guardian proxy connection from Docker containers.
- Added Aider (Scalpel) integration, successfully tested Guardian connection and volume writes.
- Added OpenCode (General) integration, using open-interpreter, configured with specific system prompts.
- Added Agent Zero (Executioner) integration, customized the Dockerfile to pre-cache compilation steps for PyPI dependencies avoiding Cython build timeouts.
- Set up and documented Continue (IDE-Glasses) endpoint configuration with generated API key (`config.yaml`).
- **Agent Zero wired to Guardian (end-to-end working).**
  - Sandbox base image upgraded to `python:3.12-slim` (AZ uses PEP 695 `type` syntax).
  - Pinned `httpx<0.28` in Dockerfile: openai 1.42 / litellm 1.44 still pass the removed `proxies` kwarg, breaking all chat completions otherwise.
  - User override is `configs/agent-zero/model_config.json` (NOT yaml — AZ's plugin system reads `config.json` for user overrides; yaml is only for bundled defaults).
  - `chat_model` and `utility_model` route through `provider: other` (generic OpenAI-compatible) → `http://host.docker.internal:11434/v1` → Guardian alias `qwen3-35b-uncensored`.
  - Compose env: `OTHER_API_KEY=${GUARDIAN_API_KEY}`, port `127.0.0.1:50001:50001`.
  - `scripts/agent_zero_up.sh` copies the JSON into `/opt/agent-zero/usr/plugins/_model_config/config.json` on each launch.
  - Verified: `models.get_chat_model(...).ainvoke(...)` returns `'OK'` from Guardian. UI live at http://127.0.0.1:50001.
