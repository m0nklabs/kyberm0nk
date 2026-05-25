# Direct CrewAI Main Quest Project Manager

This is the active KyberM0nk path for the user's main quest: direct host-native CrewAI for project-manager and planning work around NewNexus, with Superset staying the broader cockpit around the rest of the local coding stack.

Default target: NewNexus, the Unreal Engine game project in `m0nklabs/NewNexus`.

## Active Path

- Runtime bootstrap: `scripts/crewai_bootstrap.sh`
- Runtime status: `scripts/crewai_status.sh`
- Dry-run validator: `scripts/crewai_main_quest_dry_run.sh`
- Live wrapper: `scripts/crewai_main_quest_run.sh`
- Shared control path: `scripts/crewai_main_quest_control.py`
- Project config: `configs/crewai/main_quest_project/`
- Model policy: `configs/crewai/model_policy.yaml`
- Host checkout: `~/NewNexus`
- Agent Zero project metadata: `~/agentzero/usr/projects/newnexus/.a0proj`

Legacy `crewai_studio_*` scripts remain only as compatibility shims. They no longer define the active Kyber path.

## Bootstrap And Validate

```bash
scripts/crewai_bootstrap.sh
scripts/crewai_status.sh
scripts/crewai_main_quest_dry_run.sh
```

The bootstrap creates `~/crewai` with a supported local Python interpreter and installs the direct CrewAI runtime. The dry-run builds the tracked CrewAI object locally without calling a model, so YAML/provider wiring can be validated before any token spend.

## Live Control

Foreground convenience wrapper:

```bash
scripts/crewai_main_quest_run.sh
```

Shared control path:

```bash
python3 scripts/crewai_main_quest_control.py run --project-id main_quest_project
python3 scripts/crewai_main_quest_control.py start --project-id main_quest_project
python3 scripts/crewai_main_quest_control.py status --project-id main_quest_project --output json
python3 scripts/crewai_main_quest_control.py stop --project-id main_quest_project
```

The control script owns foreground runs, detached background runs, restart, stop, status, and persisted operator inputs. Terminal usage and Claude MCP usage go through the same control path so they do not drift.

Live kickoff guardrails:

- Guardian-backed runs wait for Guardian `/api/status` to go idle before they start sharing the same local GPU route.
- OpenRouter-backed live runs emit a cloud-spend warning and attempt a `/credits` balance check when the configured key supports it.
- Persisted operator inputs include `repo_write_mode` and `github_target_branch` so first pilots can stay explicitly non-destructive.

## Claude MCP Surface

The user-scoped Claude `crewai` MCP now exposes the direct tracked CrewAI lane instead of a Studio/container surface:

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

This is the safe operational slice today: inspect the tracked project, validate it through dry-run, start or stop the background run, update persisted steering between restarts, and read live log output.

## Crew Shape

The seeded crew is a fallback layout, not a hard lock. Claude may assemble or revise a different team through the CrewAI MCP when needed, but OpenRouter picks must stay inside the MoniFuse top20 value pool in `configs/crewai/model_policy.yaml` unless the operator explicitly overrides policy.

Current tracked defaults:

- Manager LLM: OpenRouter `deepseek/deepseek-v4-flash`
- Planning LLM: OpenRouter `z-ai/glm-4.7-flash`
- `main_quest_project_manager`: OpenRouter `openai/deepseek/deepseek-v4-flash`
- `local_game_researcher`: Guardian `openai/qwen3-35b-reasoning-agent`
- `local_game_builder`: Guardian `openai/qwen3-35b-uncensored-agent`
- `qa_playtest_reviewer`: OpenRouter `openai/z-ai/glm-5.1`
- `expert_escalation_engineer`: OpenRouter `openai/deepseek/deepseek-v4-pro`

When Claude selects `openai/gpt-5.4` through OpenRouter, the expected request profile is `reasoning.effort=xhigh` with returned reasoning excluded unless the run explicitly needs those blocks.

## Operator Steering

The persisted steering fields are:

- `operator_goal`: the playable slice or task to execute
- `project_path`: the active host-side NewNexus path, normally `/home/flip/NewNexus`
- `current_state`: the current known state of the project
- `operator_chat_guidance`: operator corrections, priorities, and explicit constraints
- `repo_write_mode`: `disabled` for non-destructive pilots, `enabled` only when intentional pushes are allowed
- `github_target_branch`: the GitHub branch to target when writes are enabled

True mid-run operator chat injection is still not implemented. The current supported flow is: update persisted inputs, then restart the run.

## Safety Rules

- Do not put OpenRouter or GitHub tokens in Git.
- Guardian and `llama-server` stay outside Docker.
- Use Guardian for cheap routine work and OpenRouter for management, review, or escalation.
- Stop and rerun instead of letting an obviously wrong crew keep spending tokens.
- Keep exploratory or first-pass live runs in `repo_write_mode=disabled` until repo context and validation commands have proven themselves.

## Legacy Note

The earlier `~/CrewAI-Studio` fork path is retired for active Kyber operation. Keep it only as legacy/archive material if needed for reference; the active supported path is direct CrewAI plus the existing Superset-based cockpit.

## Pilot Observation

A bounded live pilot on 2026-05-14 exposed that the original GitHub search path could return documentation mentions instead of exact Unreal files for queries such as `NewNexus.uproject`. The direct CrewAI tool now attempts an exact repository file fetch first for path-style queries, which corrected the pilot immediately.
