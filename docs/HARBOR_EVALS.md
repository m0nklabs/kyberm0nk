# Harbor Evaluations

Harbor is the cross-framework evaluation harness for Kyber's local coding stack. The live source checkout is `/home/flip/harbor`, and the installed CLI is now sourced from that checkout with an editable `uv tool` install.

## Current Local Harbor State

The local Harbor checkout already carries the framework-integration fixes Kyber needs:

- `BaseInstalledAgent` keeps `extra_env` and merges it into agent exec calls.
- `claude-code` accepts extra auth and base-url env, plus Bedrock passthrough.
- `hermes` supports native provider routing plus `OPENAI_API_BASE` passthrough.
- `aider` resolves API keys from injected env and works with Guardian-style OpenAI base URLs.

Validated on 2026-06-05 with:

```bash
cd /home/flip/harbor
uv run pytest \
  tests/unit/agents/installed/test_env_passthrough.py \
  tests/unit/agents/installed/test_hermes_cli.py \
  tests/unit/agents/installed/test_claude_code_bedrock.py \
  tests/unit/agents/installed/test_claude_code_memory.py \
  tests/unit/agents/installed/test_claude_code_mcp.py \
  tests/unit/agents/installed/test_claude_code_skills.py
uv tool install --editable --force .
```

## Standard Kyber Wrapper

Use the Kyber wrapper for direct CLI runs:

```bash
scripts/harbor_eval.sh <claude-code|hermes|aider> [harbor run args...]
```

Defaults:

- Harbor checkout: `/home/flip/harbor`
- Harbor tasks: `/home/flip/harbor/examples/tasks`
- Harbor jobs dir: `/home/flip/kyberm0nk/scratch/harbor-jobs/<agent>`
- Harbor environment: `docker`
- Local single-flight concurrency: `1`
- Docker host alias: Linux `docker0` bridge IP when available, otherwise `host.docker.internal`

The wrapper is intentionally for direct `harbor run` CLI usage. For full Harbor job configs, call Harbor directly from `/home/flip/harbor`.

## Default Local Routes

| Agent | Default model route | Base URL inside Harbor docker env | Default auth source |
|------|---------------------|-----------------------------------|---------------------|
| Claude Code | `CLAUDE_LOCAL_MODEL`, then `DEFAULT_MODEL`, then `qwen3-35b-uncensored` | `http://<detected-docker-host>:11434` | `CLAUDECODE_GUARDIAN_API_KEY`, fallback `KYBERM0NK_GUARDIAN_API_KEY` |
| Hermes | `openai/$DEFAULT_MODEL` | `http://<detected-docker-host>:11434/v1` | `KYBERM0NK_GUARDIAN_API_KEY` |
| Aider | `openai/$AIDER_LOCAL_MODEL`, fallback `openai/$DEFAULT_MODEL` | `http://<detected-docker-host>:11434/v1` | `AIDER_GUARDIAN_API_KEY`, fallback `KYBERM0NK_GUARDIAN_API_KEY` |

On Linux, the wrapper now prefers the `docker0` bridge IP automatically because plain Docker often does not resolve `host.docker.internal`. You can still override `HARBOR_DOCKER_HOST`, `HARBOR_CLAUDE_BASE_URL`, or `HARBOR_OPENAI_BASE_URL` explicitly when the host bridge differs.

## Examples

Run the default Claude lane on Harbor's example tasks:

```bash
scripts/harbor_eval.sh claude-code
```

Run Hermes against a filtered subset of example tasks:

```bash
scripts/harbor_eval.sh hermes --include-task-name write-file
```

Run Aider against an explicit local task path:

```bash
scripts/harbor_eval.sh aider --path /home/flip/harbor/examples/tasks
```

Switch the docker host alias if your engine exposes the host on a different address:

```bash
HARBOR_DOCKER_HOST=172.17.0.1 scripts/harbor_eval.sh hermes
```

## When To Use Harbor

Use Harbor when the question is comparative or operational:

- Compare Claude Code, Hermes, and Aider on the same task set.
- Validate that a framework still works after launcher or routing changes.
- Smoke-test Guardian-backed framework lanes through a reproducible harness.
- Capture repeatable job output under `scratch/harbor-jobs/` instead of one-off terminal notes.

Do not use Harbor as a replacement for normal repo work. Harbor is the harness around the frameworks, not the source workspace being edited.