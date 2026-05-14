# Scripts

Reusable helper scripts will live here.

Planned scripts:

- `health-guardian.sh`: verify Guardian from host and container.
- `run-aider.sh`: start Aider against the active project.
- `run-opencode.sh`: start OpenCode against the active project.
- `run-agent-zero.sh`: start Agent Zero with strict mounts.
- `status.sh`: show active project, model target, and tool status.
- `benchmark_guardian_context.py`: benchmark Guardian latency and GPU load across multiple context sizes.
- `render_benchmark_trends.py`: render benchmark CSV files into standalone HTML trend reports.
- `superset.sh`: wrap the sandbox Superset CLI with Kyber defaults, links, container-local state, and agent seeding.
- `superset-opencode-agent.sh`: Superset terminal-agent wrapper for OpenCode routed through Guardian.
- `superset-aider-agent.sh`: Superset terminal-agent wrapper for Aider routed through Guardian.
- `seed_superset_agents.py`: idempotently add Kyber agent rows to the local Superset host DB.
- `crewai_studio_bootstrap.sh`: clone/update the `m0nklabs/CrewAI-Studio` fork under `.agent-projects/`, write ignored runtime env, and start the Studio UI on port 8505.
- `crewai_studio_status.sh`: show CrewAI-Studio Docker status and Streamlit health.
- `crewai_studio_seed_main_quest.sh`: copy the tracked Kyber main quest crew JSON into the local Studio import folder.
- `crewai_main_quest_dry_run.sh`: copy the direct CrewAI YAML project into the Studio container and build the crew without calling models.
- `crewai_main_quest_control.py`: shared control path for the tracked CrewAI main quest with `run`, `start`, `status`, and `stop` modes.
- `ensure_newnexus_checkout.sh`: ensure the persistent local NewNexus checkout exists under `.agent-projects/NewNexus`.
- `provision_agent_zero_projects.sh`: restore tracked Agent Zero project templates into the running sandbox after rebuilds.
- `agent_zero_unstick.sh`: stop a repetitive Agent Zero UI run, reprovision tracked config, and start the UI with fresh runtime state.
- `provision_windows_unreal_ssh.sh`: copy the dedicated Windows Unreal SSH config and key into the running Agent Zero sandbox without rebuilding or recreating it.
- `test_windows_unreal_ssh.sh`: verify host and Agent Zero sandbox SSH access to the Windows Unreal executor.
- `check_mcp_registry_sync.py`: compare live `claude mcp` registrations against `configs/mcp/servers.yaml` and fail on drift when requested.
- `supervisor_tick.py`: inspect one repo plus worker slice, apply protected-path heuristics, ask Guardian for a bounded decision, and append a JSONL supervisor log entry.

Scripts must be non-interactive by default and log with timestamps where practical.

`opencode.sh` applies benchmark-based defaults from `.env`: 65536 context, 4096 max tokens, and temperature 0.2 unless overridden.
