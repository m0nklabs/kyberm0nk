# Agent Handoff Prompt

Use this prompt when opening KyberM0nk in its own workspace and assigning the next agent to continue implementation.

```text
You are working in the KyberM0nk repository.

KyberM0nk is a local agentic coding cockpit. Its job is to make the local coding-agent stack stand on its own feet as quickly as possible, while keeping Guardian and llama.cpp outside Docker.

Read these files first:

1. README.md
2. docs/ARCHITECTURE.md
3. docs/TOOL_ROLES.md
4. docs/WORKSPACE_SETUP.md
5. docs/SECURITY.md
6. docs/DOCKER_STACK.md
7. docs/TODO_LIST.md

Core rules:

- Guardian and llama-server are external infrastructure.
- Never start standalone llama-server from this repo.
- Never call backend port 11440 directly.
- Use Guardian proxy port 11434 through the OpenAI-compatible /v1 API.
- Do not edit ~/llama_cpp_guardian/config/models.yaml unless the operator explicitly asks.
- Active project mounts may be read-write.
- Reference project mounts must be read-only by default.
- Do not mount the Docker socket by default.
- Do not commit secrets.
- Keep code, docs, comments, and commits in English.

Primary objective:

Make KyberM0nk self-hosting enough that it can continue building itself with local tools.

Recommended bootstrap order:

1. Add a Guardian health-check script that works from host and Docker.
2. Add the minimal Docker/Compose foundation shared by the tools.
3. Add Aider first as a small, focused smoke test for Guardian + project editing.
4. Add OpenCode immediately after Aider as the strategic self-building agent.
5. Add Agent Zero last because it needs the strictest sandbox/mount rules.
6. Add Continue config snippets after the CLI loop is stable.

Definition of done for the first implementation pass:

- A command in scripts/ can verify Guardian from the host.
- A Docker service can verify Guardian from inside the container.
- Aider can run against the KyberM0nk repo using Guardian /v1.
- OpenCode has a documented config path and launch script, even if minimal.
- docs/TODO_LIST.md is updated with completed and next steps.
- README.md includes the new quick-start commands.
- All changes are committed and pushed to m0nklabs/kyberm0nk.

Be conservative: create the smallest working loop first, then let KyberM0nk grow from there.
```

## Bootstrap Decision

Aider should be installed first only as a smoke-test layer, not as the main brain.

OpenCode should become the first strategic tool because KyberM0nk's goal is autonomous planning and self-building. Aider proves that the Guardian endpoint, model alias, mount policy, and edit loop work before giving the larger strategist more moving parts.
