# KyberM0nk

Local agentic coding cockpit powered by Guardian.

KyberM0nk is the control workspace for a local coding-agent stack. It coordinates open-source coding tools around the existing Guardian proxy and llama.cpp backend, without owning model files or starting standalone inference servers.

## Core Idea

- Guardian and `llama-server` stay outside Docker.
- Agent tools run in isolated Docker containers where practical.
- Continue stays in the IDE as an extension, configured against Guardian.
- Active projects mount read-write only when explicitly selected.
- Reference repositories mount read-only by default.
- The Docker socket is not mounted by default.

## Initial Stack

| Role | Tool | Purpose |
|------|------|---------|
| Strategist | OpenCode | High-level planning, task decomposition, architecture work |
| Scalpel | Aider | Focused code edits in an active project workspace |
| Lens | Continue | IDE chat and inline assistance against local Guardian models |
| Operator | Agent Zero | Sandboxed system tasks, scripts, environment debugging |
| Gatekeeper | Guardian | OpenAI-compatible broker for local models |
| Engine | llama.cpp | GPU inference backend managed by Guardian |

## Intended Default Model

The initial local model target is Guardian alias `qwen3-35b-uncensored`, which currently resolves to `Qwen3.6-35B-A3B-HauhauCS-Aggressive` in Guardian.

KyberM0nk must not edit Guardian model settings automatically. Model loading, pinning, tensor split, context, and VRAM policy remain owned by `~/llama_cpp_guardian/config/models.yaml`.

## Documentation

Start here:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/TOOL_ROLES.md](docs/TOOL_ROLES.md)
- [docs/WORKSPACE_SETUP.md](docs/WORKSPACE_SETUP.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/TODO_LIST.md](docs/TODO_LIST.md)

## Repository Status

This repository starts as a documentation-first planning workspace. Implementation should be added in small, testable steps after the workspace is opened directly.
