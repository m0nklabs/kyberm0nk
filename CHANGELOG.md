# Changelog

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
