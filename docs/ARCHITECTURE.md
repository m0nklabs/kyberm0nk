# Architecture

## Summary

KyberM0nk is a local agentic coding cockpit. It separates inference infrastructure from tool orchestration.

```text
+------------------------------+
| VS Code / Terminal Operator  |
+---------------+--------------+
                |
                v
+------------------------------+
| KyberM0nk Workspace          |
| - docs                       |
| - configs                    |
| - scripts                    |
| - Docker Compose stack       |
+---+------------+-------------+
    |            |
    |            +------------------+
    v                               v
+-----------+                +-------------+
| OpenCode  |                | Agent Zero  |
+-----------+                +-------------+
    |                               |
    v                               v
+-----------+                +-------------+
| Aider     |                | Tool shell  |
+-----------+                +-------------+
    |
    v
+------------------------------+
| Guardian proxy                |
| http://host.docker.internal   |
| :11434/v1                     |
+------------------------------+
                |
                v
+------------------------------+
| llama.cpp backend             |
| 127.0.0.1:11440               |
| Managed by Guardian only      |
+------------------------------+
```

## Boundary Decisions

### Outside Docker

- Guardian proxy
- `llama-server`
- GGUF model files
- GPU allocation and tensor split policy
- VS Code Continue extension

### Inside Docker

- Aider runtime
- OpenCode runtime, if Docker-friendly
- Agent Zero runtime
- shared CLI dependencies
- temporary working shells

## Mount Model

The stack should use three mount categories:

| Mount | Access | Purpose |
|-------|--------|---------|
| Active project | read-write | The project being edited |
| Reference projects | read-only | Context and pattern lookup |
| KyberM0nk config | read-only or read-write per service | Tool config and logs |

The default must avoid accidental write access to reference repositories.

## Model Routing

All tools should use an OpenAI-compatible endpoint:

```text
GUARDIAN_BASE_URL=http://host.docker.internal:11434/v1
```

The initial deep model alias is:

```text
qwen3-35b-uncensored
```

Guardian remains the source of truth for actual model paths, context sizes, VRAM policy, pinned model behavior, and switch allowlists.

## Agent Model Budgets

KyberM0nk tools should use balanced coding-agent budgets rather than maximum stress-test budgets.

Default policy:

- OpenCode: `65536` context, `4096` max tokens, `0.2` temperature.
- Agent Zero chat: `65536` context with `ctx_history: 0.35`, `1536` output cap, and `240s` timeout.
- Agent Zero utility: `32768` context with `ctx_input: 0.35`, `1024` output cap, and `180s` timeout.
- Avoid `32768` output-token caps for normal autonomous coding tasks.

The benchmark suite and trend renderer in `scripts/` provide the evidence trail for changing these values.

## Non-Goals

- KyberM0nk does not replace Guardian.
- KyberM0nk does not download or manage GGUF model files.
- KyberM0nk does not start direct `llama-server` processes.
- KyberM0nk does not replace project-specific workspaces; it coordinates frameworks around them. See [WORKSPACE_POLICY.md](WORKSPACE_POLICY.md).
