# Scripts

Reusable helper scripts live here.

Key active scripts:

- `health-guardian.sh`: verify Guardian from the host runtime.
- `run-aider.sh`: start Aider against the active project.
- `aider_advisor.py`: daily-gated OpenRouter GPT-5.5 advisor lane for difficult questions.
- `run-opencode.sh`: start OpenCode against the active project.
- `run-agent-zero.sh`: start Agent Zero with isolated host runtime paths.
- `status.sh`: show active project, model target, and tool status.
- `benchmark_guardian_context.py`: benchmark Guardian latency and GPU load across multiple context sizes.
- `render_benchmark_trends.py`: render benchmark CSV files into standalone HTML trend reports.
- `superset.sh`: wrap the host-native Superset CLI with Kyber defaults, links, local state, and agent seeding.
- `superset_bootstrap.sh`: move or bootstrap the active Superset checkout into `~/superset`.
- `superset-opencode-agent.sh`: Superset terminal-agent wrapper for OpenCode routed through Guardian.
- `superset-aider-agent.sh`: Superset terminal-agent wrapper for Aider routed through Guardian.
- `seed_superset_agents.py`: idempotently add Kyber agent rows to the local Superset host DB.
- `bootstrap_host_workers.sh`: create the host-native Aider runtime under `~/aider` plus the isolated OpenCode worker venv under `~/venvs/kyber-workers`.
- `crewai_bootstrap.sh`: create or update the direct host-native CrewAI runtime in `~/crewai` with a supported local Python interpreter.
- `crewai_status.sh`: show direct CrewAI runtime readiness plus tracked controller status.
- `crewai_studio_bootstrap.sh`: compatibility wrapper that now bootstraps the direct CrewAI runtime instead of reviving Studio.
- `crewai_studio_status.sh`: compatibility wrapper that now shows direct CrewAI status instead of Studio container health.
- `crewai_studio_seed_main_quest.sh`: compatibility no-op because the direct CrewAI lane does not use a Studio database seed step.
- `crewai_main_quest_dry_run.sh`: build the direct CrewAI YAML project locally without calling models.
- `crewai_main_quest_control.py`: shared control path for the tracked direct CrewAI main quest with `run`, `start`, `restart`, `status`, `stop`, `get-inputs`, and `set-inputs` modes, including persisted `repo_write_mode` and `github_target_branch` safety inputs for live pilots.
- `ensure_newnexus_checkout.sh`: ensure the persistent local NewNexus checkout exists at `~/NewNexus`.
- `provision_agent_zero_projects.sh`: restore tracked Agent Zero project templates into the host runtime after bootstrap or restart.
- `agent_zero_unstick.sh`: stop a repetitive Agent Zero UI run, reprovision tracked config, and start the UI with fresh runtime state.
- `provision_windows_unreal_ssh.sh`: copy the dedicated Windows Unreal SSH config and key into the running Agent Zero runtime without rebuilding or recreating it.
- `test_windows_unreal_ssh.sh`: verify host and Agent Zero runtime SSH access to the Windows Unreal executor.
- `check_mcp_registry_sync.py`: compare live `claude mcp` registrations against `configs/mcp/servers.yaml` and fail on drift when requested.
- `hermes_queue_watchdog.py`: read the Hermes `issue_runs` SQLite queue, report stale `running` rows, old `queued` rows, queue-depth pressure, recent failures, and append JSONL improvement signals.
- `supervisor_tick.py`: inspect one repo plus worker slice, apply protected-path heuristics, ask Guardian for a bounded decision, and append a JSONL supervisor log entry.
- `validate_docs.sh`: validate the current docs surface, local Markdown links, required docs artifacts, and basic `kyber-tag` schema hygiene.
- `validate_kyber_tag_schema.py`: validate the PR routing tag schema and bundled examples for fail-closed review-loop routing.
- `test_quickstart.sh`: run the lightweight quickstart smoke sequence for docs (`validate_docs` + expected success output).

Scripts must be non-interactive by default and log with timestamps where practical.

`opencode.sh` applies benchmark-based defaults from `.env`: 65536 context, 4096 max tokens, and temperature 0.2 unless overridden.
