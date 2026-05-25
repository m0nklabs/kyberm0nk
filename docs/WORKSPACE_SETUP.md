# Workspace Setup

## Recommended Local Path

```text
/home/flip/kyberm0nk
```

## VS Code Workspace

Open the project as its own workspace, not from the home directory workspace.

Recommended workspace file:

```text
/home/flip/kyberm0nk.code-workspace
```

It should include only:

```json
{
  "folders": [
    {
      "path": "kyberm0nk"
    }
  ]
}
```

## Workspace-First Rule

Treat every agentic framework the way VS Code treats a workspace: bind it to one explicit project root instead of letting it drift across the home directory or a hidden copy.

- Kyber is the control workspace.
- The repo being edited is the source workspace.
- Framework-specific state may live elsewhere, but it should still point back to that same source workspace.

See [WORKSPACE_POLICY.md](WORKSPACE_POLICY.md) for the detailed rule and per-framework mapping.

See [WORKSPACE_INVENTORY.md](WORKSPACE_INVENTORY.md) for the current distinction between real repo checkouts, runtime roots, and local lab directories in this workspace.

The shared multi-root `kyberm0nk.code-workspace` should point at the real framework checkouts `~/aider`, `~/crewAI`, `~/opencode`, and `~/langgraph` instead of the old runtime/lab paths `~/crewai`, `~/.opencode`, and `~/langgraph-lab`.

## Environment

Copy `.env.example` to `.env` and fill local values.

Important variables:

| Variable | Purpose |
|----------|---------|
| `GUARDIAN_BASE_URL` | OpenAI-compatible Guardian endpoint |
| `GUARDIAN_API_KEY` | Bearer token for Guardian |
| `DEFAULT_MODEL` | Default Guardian model alias |
| `ACTIVE_PROJECT` | Project mounted read-write |
| `REFERENCE_PROJECTS` | Comma-separated reference paths used by wrappers and helper tooling |
| `AIDER_ROOT` | Host-native Aider runtime root |
| `KYBER_WORKERS_VENV_DIR` | Host-native worker root for the OpenCode runtime and stable worker entrypoints |
| `SUPERSET_ROOT` | Host checkout for Superset |
| `SUPERSET_HOME_DIR` | Host-local Superset state directory |
| `AGENT_ZERO_ROOT` | Host checkout for Agent Zero |
| `WINDOWS_UNREAL_SSH_KEY_PATH` | Host path to the dedicated Windows Unreal SSH private key |
| `WINDOWS_UNREAL_SSH_ALIAS` | SSH alias exposed to tools for the Windows Unreal executor |
| `ALLOW_DOCKER_SOCKET` | Must stay false unless an exceptional container task is explicitly needed |

For an already-running Agent Zero host runtime, use `scripts/provision_windows_unreal_ssh.sh` to copy the Windows Unreal SSH config and dedicated key into the isolated runtime without rebuilding the checkout or recreating the runtime tree.

Tracked Agent Zero projects live under `configs/agent-zero/projects/`. `scripts/agent_zero_up.sh` calls `scripts/provision_agent_zero_projects.sh` so project metadata is restored after a host runtime refresh without overwriting an existing runtime project unless `--force` is used.

The `NewNexus` Agent Zero project is restored from `configs/agent-zero/projects/newnexus`. The actual source checkout stays at `~/NewNexus`, while Agent Zero-specific project metadata is restored under `~/agentzero/usr/projects/newnexus/.a0proj`.

## First Implementation Steps

1. Open the new workspace.
2. Verify Guardian health from the host.
3. Clone or refresh upstream framework repos under their real names such as `~/aider`, `~/crewAI`, `~/opencode`, and `~/langgraph`.
4. Bootstrap Aider into `~/aider` and the remaining host worker runtimes with `scripts/bootstrap_host_workers.sh`.
5. Bootstrap Superset into `~/superset` and login on the host.
6. Bootstrap Agent Zero into `~/agentzero` and validate `scripts/agent_zero_up.sh`.
7. Bootstrap direct CrewAI into `~/crewai`.
8. Configure Continue separately in VS Code.

## Success Criteria

The workspace is ready when:

- GitHub remote exists under `m0nklabs/kyberm0nk`.
- The initial docs are pushed.
- `.env.example` documents all required local variables.
- No secrets are committed.
- The first host-native worker checks can reach Guardian via `/v1`.
