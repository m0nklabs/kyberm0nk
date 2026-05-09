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

## Environment

Copy `.env.example` to `.env` and fill local values.

Important variables:

| Variable | Purpose |
|----------|---------|
| `GUARDIAN_BASE_URL` | OpenAI-compatible Guardian endpoint |
| `GUARDIAN_API_KEY` | Bearer token for Guardian |
| `DEFAULT_MODEL` | Default Guardian model alias |
| `ACTIVE_PROJECT` | Project mounted read-write |
| `REFERENCE_PROJECTS` | Comma-separated read-only reference mounts |
| `WINDOWS_UNREAL_SSH_KEY_PATH` | Host path to the dedicated Windows Unreal SSH private key |
| `WINDOWS_UNREAL_SSH_ALIAS` | SSH alias exposed to tools for the Windows Unreal executor |
| `ALLOW_DOCKER_SOCKET` | Must stay false unless explicitly needed |

For an already-running Agent Zero sandbox, use `scripts/provision_windows_unreal_ssh.sh` to copy the Windows Unreal SSH config and dedicated key into the container without rebuilding the image or recreating Agent Zero.

## First Implementation Steps

1. Open the new workspace.
2. Verify Guardian health from the host.
3. Verify Guardian health from inside a minimal Docker container.
4. Add the Aider container first as the smallest Guardian/edit-loop smoke test.
5. Add OpenCode immediately after Aider as the strategic self-building agent.
6. Add Agent Zero last, with strict mount rules.
7. Configure Continue separately in VS Code.

## Success Criteria

The workspace is ready when:

- GitHub remote exists under `m0nklabs/kyberm0nk`.
- The initial docs are pushed.
- `.env.example` documents all required local variables.
- No secrets are committed.
- The first Docker health check can reach Guardian via `/v1`.
