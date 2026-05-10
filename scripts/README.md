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
- `ensure_newnexus_checkout.sh`: ensure the persistent local NewNexus checkout exists under `.agent-projects/NewNexus`.
- `provision_agent_zero_projects.sh`: restore tracked Agent Zero project templates into the running sandbox after rebuilds.
- `agent_zero_unstick.sh`: stop a repetitive Agent Zero UI run, reprovision tracked config, and start the UI with fresh runtime state.
- `provision_windows_unreal_ssh.sh`: copy the dedicated Windows Unreal SSH config and key into the running Agent Zero sandbox without rebuilding or recreating it.
- `test_windows_unreal_ssh.sh`: verify host and Agent Zero sandbox SSH access to the Windows Unreal executor.

Scripts must be non-interactive by default and log with timestamps where practical.

`opencode.sh` applies benchmark-based defaults from `.env`: 65536 context, 4096 max tokens, and temperature 0.2 unless overridden.
