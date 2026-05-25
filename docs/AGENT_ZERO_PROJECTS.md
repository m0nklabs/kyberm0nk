# Agent Zero Projects

Agent Zero project metadata is container runtime state by default. A Docker rebuild or recreated sandbox can remove it, so durable project templates are tracked here:

```text
configs/agent-zero/projects/<project-slug>/.a0proj/
```

## Restore Flow

Run:

```bash
scripts/provision_agent_zero_projects.sh
```

The script starts the existing sandbox if needed, copies missing tracked project templates into `/opt/agent-zero/usr/projects/`, and creates the corresponding `/a0/usr/projects/` workspace entry.

The restore flow provisions only deprecated compatibility stubs for the old NewNexus-specific Windows command names. They exit with a message and do not perform validation. Agent Zero must generate the Windows SSH, PowerShell, Git, and UnrealBuildTool commands itself from the project instructions and known paths.

GitHub push access is provisioned separately because it depends on a local secret token. Put a fresh GitHub token in:

```text
/home/flip/.secrets/kyberm0nk_github_token
```

Then run:

```bash
scripts/provision_agent_zero_github.sh
```

The script copies only that token into `/run/kyberm0nk/secrets/github_token` inside the running sandbox and installs a Git credential helper. It keeps tokens out of remotes, logs, and tracked files. It may run a silent `git push --dry-run` to verify credentials, but it must not update remote refs during provisioning.

Use `--force` only when the tracked template should overwrite the current runtime metadata:

```bash
scripts/provision_agent_zero_projects.sh --force
```

## NewNexus

The tracked `newnexus` project restores:

- Agent Zero project title and instructions.
- Project model config matching the current Guardian `gemma4-26b-agent` route.
- Project knowledge and instruction files.
- Project metadata under `~/agentzero/usr/projects/newnexus/.a0proj`.

The source checkout is not committed to KyberM0nk. It lives at `~/NewNexus`, which is the normal host clone of `https://github.com/m0nklabs/NewNexus.git`.

Agent Zero should commit and push NewNexus changes from `/home/flip/NewNexus` through the host runtime credential helper. The Windows checkout is only for pulling those commits and running Unreal build/editor validation through direct `ssh unreal-windows` commands.

The host-native setup no longer requires a NewNexus source symlink under `/a0/usr/projects/newnexus`. The repository stays at `~/NewNexus`, and only the Agent Zero project metadata is restored under `~/agentzero/usr/projects/newnexus/.a0proj`.

For Windows validation, the project instructions point Agent Zero at:

```text
J:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe
```