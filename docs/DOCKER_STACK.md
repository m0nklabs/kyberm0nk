# Docker Stack Plan

This file describes the intended Docker Compose stack. The actual `docker-compose.yml` should be added only after the first tool image is verified.

## Services

### aider

Purpose: focused code edits against the active project.

Required environment:

```text
OPENAI_API_BASE=${GUARDIAN_BASE_URL}
OPENAI_API_KEY=${AIDER_GUARDIAN_API_KEY}
AIDER_MODEL=${DEFAULT_MODEL}
```

Mounts:

```text
${ACTIVE_PROJECT}:/workspace/project:rw
./configs/aider:/config/aider:ro
./logs/aider:/logs/aider:rw
```

### opencode

Purpose: strategic planning and architecture work.

Mounts should match Aider, but reference repositories may be more important for this service.

### agent-zero

Purpose: sandboxed system and script tasks.

Required environment:

```text
OTHER_API_KEY=${AGENT_ZERO_GUARDIAN_API_KEY}
```

Agent Zero should get the narrowest mount set possible for each task.

### guardian-health

Purpose: verify container-to-host Guardian connectivity before launching heavy tools.

This can be a lightweight curl-based container.

## Host Gateway

On Linux, Compose should include:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Not Included

The stack must not include:

- `llama-server`
- Ollama
- Guardian
- GGUF model volumes
- Docker socket by default
