# CrewAI-Studio Main Quest Project Manager

This is the KyberM0nk path for the user's main quest: a visible CrewAI-Studio project manager that can drive game-development work while the operator watches and steers the run.

## What Exists Now

- Fork: `m0nklabs/CrewAI-Studio`, based on `strnad/CrewAI-Studio`.
- Local checkout path: `.agent-projects/CrewAI-Studio`.
- Studio UI: Streamlit on port `8505` by default.
- Cloud models: OpenRouter through the fork's dedicated `OpenRouter` provider.
- Local models: Guardian through the fork's dedicated `Guardian` provider.
- Crew seed: `configs/crewai/main_quest_studio_import.json`.
- Model policy: `configs/crewai/model_policy.yaml`.

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

The bootstrap script keeps secrets in the ignored fork checkout `.env`. It can read `OPENROUTER_API_KEY` from Kyber's `.env` or from `OPENROUTER_API_KEY_FILE`, defaulting to `$HOME/.secrets/openrouter.key` when present.

## Seed The Main Quest Crew

```bash
scripts/crewai_studio_seed_main_quest.sh
```

Then open CrewAI-Studio, go to Import/Export, and import:

```text
.agent-projects/CrewAI-Studio/kyber-imports/main_quest_studio_import.json
```

## Crew Shape

| Role | Provider | Model | Purpose |
|------|----------|-------|---------|
| Main Quest Project Manager | OpenRouter | `deepseek/deepseek-v4-pro` | Breaks the game goal into milestones, delegates, and gates escalation. |
| Planner | OpenRouter | `deepseek/deepseek-v4-flash` | Cheap planning and run summaries. |
| Local Game Researcher | Guardian | `gemma4-26b-agent` | Local context gathering and summarization. |
| Local Game Builder | Guardian | `qwen3-35b-reasoning-agent` | Routine implementation planning and patch drafting. |
| QA Playtest Reviewer | OpenRouter | `google/gemini-3.1-pro-preview-customtools` | Final review, regression risk, and acceptance checks. |
| Expert Escalation Engineer | OpenRouter | `moonshotai/kimi-k2.6` | Narrow blocker escalation after local failure. |

## Operator Steering

The seeded crew includes an `operator_chat_guidance` placeholder. Use it as the steering channel for the current run: paste corrections, priorities, constraints, and course changes there before kickoff.

Current limitation: upstream CrewAI-Studio does not provide true mid-run chat injection into an active CrewAI execution. The usable first version is watchable and steerable between runs: stop a wrong run, update `operator_chat_guidance`, and restart from the latest result. A dedicated live steering panel/tool is the next fork improvement.

## First Game Run Inputs

Use these placeholders in the kickoff screen:

- `operator_goal`: the game feature or playable slice to build.
- `project_path`: the active project path, for example `/workspace/project`.
- `current_state`: a short summary of what already exists.
- `operator_chat_guidance`: live direction from the operator, including what to avoid.

## Safety Rules

- Do not put OpenRouter keys in Git.
- Keep the CrewAI-Studio checkout under `.agent-projects/`.
- Guardian and `llama-server` stay outside Docker.
- Use Guardian for cheap routine work and OpenRouter only for management, review, or escalation.
- Stop and rerun instead of letting an obviously wrong crew continue spending tokens.
