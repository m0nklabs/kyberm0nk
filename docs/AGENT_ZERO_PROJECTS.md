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

Use `--force` only when the tracked template should overwrite the current runtime metadata:

```bash
scripts/provision_agent_zero_projects.sh --force
```

## NewNexus

The tracked `newnexus` project restores:

- Agent Zero project title and instructions.
- Project model config matching the current Guardian `gemma4-agent` route.
- Project knowledge and instruction files.
- A stable `/a0/usr/projects/newnexus` workspace path.

The source checkout is not committed to KyberM0nk. It lives under `.agent-projects/NewNexus`, which is ignored by Git and is a normal clone of `https://github.com/m0nklabs/NewNexus.git`.

The workspace path is restored as:

```text
/a0/usr/projects/newnexus -> /workspace/project/.agent-projects/NewNexus
```

That gives Agent Zero a stable project workspace while the actual game source remains in the NewNexus repository.