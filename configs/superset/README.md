# Superset Integration

Superset is the preferred KyberM0nk session/worktree cockpit candidate.

Links:

- Website: https://superset.sh
- Docs: https://docs.superset.sh
- Repository: https://github.com/superset-sh/superset
- CLI install script: https://superset.sh/cli/install.sh

Kyber wraps Superset through `scripts/superset.sh`.

The active wrapper is host-native. It expects the Superset checkout at `~/superset` and uses `~/.superset` for local CLI and host-service state.

## Local State

By default Kyber stores Superset CLI/host state on the host at:

```text
~/.superset/
```

The active project is imported from its real host path. Use the wrapper instead of raw Superset commands so Kyber defaults, agent presets, and host-worker paths stay consistent.

Bootstrap or move the checkout with:

```bash
scripts/superset_bootstrap.sh
scripts/superset.sh link
scripts/superset.sh login
```

## Agent Presets

Run this after Superset login/start has created a local host database:

```bash
scripts/superset.sh seed-agents
```

That adds or updates:

| Preset | Command | Prompt |
| --- | --- | --- |
| `kyber-opencode` | `scripts/superset-opencode-agent.sh` | stdin |
| `kyber-aider` | `scripts/superset-aider-agent.sh` | stdin |
| `kyber-claude-code` | `claude --permission-mode bypassPermissions` | argv, only when Claude Code is installed unless forced |

The OpenCode and Aider wrappers run from the Kyber host workspace and route model calls through Guardian via the host worker venv at `~/venvs/kyber-workers`.

## Live Smoke

Current host-native operator flow:

```bash
scripts/superset.sh status
scripts/superset.sh start
scripts/superset.sh seed-agents
scripts/superset.sh import-active
```

The host-native wrapper has already been validated through `link` and `status`; a fresh machine still needs `scripts/superset.sh login` before project import and worktree commands can proceed.
