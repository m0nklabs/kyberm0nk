# Superset Integration

Superset is the preferred KyberM0nk session/worktree cockpit candidate.

Links:

- Website: https://superset.sh
- Docs: https://docs.superset.sh
- Repository: https://github.com/superset-sh/superset
- CLI install script: https://superset.sh/cli/install.sh

Kyber wraps Superset through `scripts/superset.sh`.

The current wrapper runs Superset inside the `kyberm0nk-sandbox-1` Docker container. The sandbox image provides the full Linux distribution bundle at `/usr/local/superset`, so the CLI has both `bin/superset` and the sibling `bin/superset-host` launcher required by `superset start`.

## Local State

By default Kyber stores Superset CLI/host state inside the sandbox container at:

```text
/root/.superset/
```

The active project is mounted into the sandbox as `/workspace/project`. Use the wrapper instead of host-side Superset commands so agent presets and imported projects reference container paths consistently.

## Agent Presets

Run this after Superset login/start has created a local host database:

```bash
scripts/superset.sh seed-agents
```

That adds or updates:

| Preset | Command | Prompt |
| --- | --- | --- |
| `kyber-opencode` | `/workspace/project/scripts/superset-opencode-agent.sh` | stdin |
| `kyber-aider` | `/workspace/project/scripts/superset-aider-agent.sh` | stdin |
| `kyber-claude-code` | `claude --permission-mode bypassPermissions` | argv, only when Claude Code is installed unless forced |

The OpenCode and Aider wrappers run from the mounted Kyber workspace and route model calls through Guardian.

## Live Smoke

The authenticated local smoke passed on 2026-05-09:

```bash
scripts/superset.sh start
scripts/superset.sh seed-agents
scripts/superset.sh import-active
scripts/superset.sh passthrough workspaces create --local --project <project-id> --name kyber-superset-smoke --branch kyber/superset-smoke --base-branch main --json
```

Superset created the disposable worktree under `/root/.superset/worktrees/<project-id>/kyber/superset-smoke` inside the sandbox.
