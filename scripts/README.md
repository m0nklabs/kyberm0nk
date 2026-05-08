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

Scripts must be non-interactive by default and log with timestamps where practical.

`opencode.sh` applies benchmark-based defaults from `.env`: 65536 context, 4096 max tokens, and temperature 0.2 unless overridden.
