# CrewAI-Studio Main Quest Project Manager

This is the KyberM0nk path for the user's main quest: a visible CrewAI-Studio project manager that can drive game-development work while the operator watches and steers the run.

Default target: NewNexus, the Unreal Engine game project in `m0nklabs/NewNexus`.

## What Exists Now

- Fork: `m0nklabs/CrewAI-Studio`, based on `strnad/CrewAI-Studio`.
- Local checkout path: `.agent-projects/CrewAI-Studio`.
- Studio UI: Streamlit on port `8505` by default.
- Cloud models: OpenRouter through the fork's dedicated `OpenRouter` provider.
- Local models: Guardian through the fork's dedicated `Guardian` provider.
- Crew seed: `configs/crewai/main_quest_studio_import.json`.
- Direct CrewAI project config: `configs/crewai/main_quest_project/`.
- Model policy: `configs/crewai/model_policy.yaml`.
- NewNexus source checkout: `.agent-projects/NewNexus` on the host and `/a0/usr/projects/newnexus` in Agent Zero.
- Repository tool: `GithubSearchTool` in the Studio UI, backed by Kyber's lightweight GitHub REST implementation scoped to `m0nklabs/NewNexus`, with the token read from `GITHUB_TOKEN` or `GH_TOKEN` in the ignored Studio `.env`.

## Why The Fork Exists

Upstream CrewAI-Studio only had a generic OpenAI-compatible provider and did not cleanly expose OpenRouter cloud models and Guardian local models side by side in the same crew. The fork adds separate providers so a manager can choose cloud escalation while routine workers stay local.

Fork improvements:

- `OpenRouter` provider with `OPENROUTER_API_KEY`, `OPENROUTER_API_BASE`, and `OPENROUTER_MODELS`.
- `Guardian` provider with `GUARDIAN_API_KEY`, `GUARDIAN_API_BASE`, and `GUARDIAN_MODELS`.
- `.env` is loaded before model lists are built, so venv and Docker runs both see configured model menus.
- Docker Compose exposes configurable ports and maps `host.docker.internal` to the Linux host for Guardian access.

## Start Studio

```bash
scripts/crewai_studio_bootstrap.sh
scripts/crewai_studio_status.sh
```

Default URLs:

- Host: `http://127.0.0.1:8505`
- LAN: `http://192.168.1.35:8505`

If `8505` is already in use, the bootstrap script automatically selects the next free port and writes that port into the ignored Studio `.env` when regeneration is enabled.

The bootstrap script keeps secrets in the ignored fork checkout `.env`. It can read `OPENROUTER_API_KEY` from Kyber's `.env` or from `OPENROUTER_API_KEY_FILE`, defaulting to `$HOME/.secrets/openrouter.key` and then `$HOME/.secrets/keys/openrouter.key` when present. The NewNexus GitHub tool reads `GITHUB_TOKEN` from the environment or `GITHUB_TOKEN_FILE`, defaulting to `$HOME/.secrets/kyberm0nk_github_token`.

## Seed The Main Quest Crew

```bash
scripts/crewai_studio_seed_main_quest.sh
```

The seed script copies the JSON into the ignored checkout and installs it directly into the running CrewAI-Studio database when the web container is up.

Manual fallback: open CrewAI-Studio, go to Import/Export, and import:

```text
.agent-projects/CrewAI-Studio/kyber-imports/main_quest_studio_import.json
```

## Direct CrewAI Dry Run

The same crew also exists as plain CrewAI config files under `configs/crewai/main_quest_project/`.

```bash
scripts/crewai_main_quest_dry_run.sh
```

This copies the config into the Studio container and builds the CrewAI `Crew` object without calling a model. It verifies that the YAML config, provider policy, and CrewAI object construction all work before spending tokens.

## Claude MCP Surface

The user-scoped Claude `crewai` MCP is no longer only a rulebook. The Kyber-vendored server now exposes a read-mostly project surface for the tracked CrewAI setup:

- `list_kyber_crewai_projects`
- `inspect_kyber_crewai_project`
- `run_kyber_crewai_dry_run`
- `get_kyber_crewai_run_status`
- `start_kyber_crewai_live_run`
- `restart_kyber_crewai_live_run`
- `get_kyber_crewai_operator_inputs`
- `update_kyber_crewai_operator_inputs`
- `stop_kyber_crewai_live_run`
- `get_kyber_crewai_live_log_preview`

This is the current safe operational slice: Claude can inspect the tracked CrewAI project, validate wiring through the existing dry-run script, start or stop the tracked background run, update the persisted operator guidance used for the next restart, and review current run/log state without going through the Studio UI manually. True mid-run steering remains separate follow-up work.

## Run Control

The tracked shell entry point [scripts/crewai_main_quest_run.sh](/home/flip/kyberm0nk/scripts/crewai_main_quest_run.sh) now delegates to [scripts/crewai_main_quest_control.py](/home/flip/kyberm0nk/scripts/crewai_main_quest_control.py), which provides:

- `run` for foreground execution
- `start` for detached background execution
- `status` for persisted PID/state inspection
- `stop` for controlled termination

The MCP uses the same control script, so terminal usage and Claude usage share one control path instead of drifting into separate wrappers.

The same control path now also exposes:

- `get-inputs` for current persisted operator inputs
- `set-inputs` for steering updates between runs
- `restart` for applying updated guidance to a fresh background run

The tracked inputs now also include `repo_write_mode` and `github_target_branch`. The current safe default is `repo_write_mode=disabled`, which lets the crew run a live research/plan/patched-output pilot without blindly committing back to `m0nklabs/NewNexus`.

## Crew Shape

The table below describes the seeded fallback crew, not a hard lock. Claude may assemble or revise a different team through the CrewAI MCP when needed, but OpenRouter picks must stay inside the MoniFuse top20 value pool in `configs/crewai/model_policy.yaml` unless the operator explicitly overrides policy. If Claude chooses `openai/gpt-5.4`, it should request `reasoning.effort=xhigh` through OpenRouter rather than using GPT-5.4 as a plain no-reasoning pass.

| Role | Provider | Model | Purpose |
|------|----------|-------|---------|
| Main Quest Project Manager | OpenRouter | `deepseek/deepseek-v4-flash` | Breaks the game goal into milestones, delegates, and gates escalation. |
| Planner | OpenRouter | `z-ai/glm-4.7-flash` | Cheap planning and run summaries. |
| Local Game Researcher | Guardian | `gemma4-26b-agent` | Local context gathering and summarization. |
| Local Game Builder | Guardian | `qwen3-35b-reasoning-agent` | Routine implementation planning and patch drafting. |
| QA Playtest Reviewer | OpenRouter | `z-ai/glm-5.1` | Final review, regression risk, and acceptance checks. |
| Expert Escalation Engineer | OpenRouter | `deepseek/deepseek-v4-pro` | Narrow blocker escalation after local failure. |

Allowed cloud pool for Claude-built crews via CrewAI MCP:

- `deepseek/deepseek-v4-flash`
- `deepseek/deepseek-v4-pro`
- `z-ai/glm-4.7-flash`
- `moonshotai/kimi-k2.5`
- `moonshotai/kimi-k2.6`
- `google/gemini-3-flash-preview`
- `deepseek/deepseek-v3.2-speciale`
- `z-ai/glm-5.1`
- `google/gemini-3.1-pro-preview-customtools`
- `openai/gpt-5.2`

## Operator Steering

The seeded crew includes an `operator_chat_guidance` placeholder. Use it as the steering channel for the current run: paste corrections, priorities, constraints, and course changes there before kickoff.

For safe pilots, also set:

- `repo_write_mode`: `disabled` for no-write runs, `enabled` only when an intentional push is allowed.
- `github_target_branch`: the branch the GitHub push tool should target if writes are enabled.

Current limitation: upstream CrewAI-Studio does not provide true mid-run chat injection into an active CrewAI execution. The usable current version is watchable and steerable between runs through the shared control path and MCP tools: update the persisted operator inputs, then restart the run. A dedicated live steering panel/tool is the next fork improvement.

## First Game Run Inputs

Use these placeholders in the kickoff screen:

- `operator_goal`: the game feature or playable slice to build.
- `project_path`: the active NewNexus project path, for example `/workspace/project/.agent-projects/NewNexus` or `/a0/usr/projects/newnexus`.
- `current_state`: a short summary of what already exists.
- `operator_chat_guidance`: live direction from the operator, including what to avoid. Mention `Stay on Unreal/NewNexus` when the run must not drift into Unity, generic 2D, or another engine.
- `repo_write_mode`: whether the current run may push to GitHub or must stay non-destructive.
- `github_target_branch`: the intended GitHub branch when writes are enabled.

## Safety Rules

- Do not put OpenRouter keys in Git.
- Keep the CrewAI-Studio checkout under `.agent-projects/`.
- Guardian and `llama-server` stay outside Docker.
- Use Guardian for cheap routine work and OpenRouter only for management, review, or escalation.
- Stop and rerun instead of letting an obviously wrong crew continue spending tokens.
- Keep exploratory or first-pass live runs in `repo_write_mode=disabled` until the crew has proven that its repo context and validation commands are sound.

## Pilot Observation

A bounded live pilot on 2026-05-14 exposed that the original GitHub search path could return documentation mentions instead of exact Unreal files for queries such as `NewNexus.uproject`. The direct CrewAI tool now attempts an exact repository file fetch first for path/filename-style queries, which corrected the pilot immediately: the rerun retrieved the real `NewNexus.uproject` with `EngineAssociation: 5.7` and plugin/module preview instead of a docs hit.
