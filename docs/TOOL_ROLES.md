# Tool Roles

KyberM0nk is not a single autonomous agent. It is a control surface for a small set of specialized tools.

## Strategist - OpenCode

OpenCode is the high-level planning and architecture tool.

Use it for:

- multi-file project planning
- feature decomposition
- architectural decisions
- cross-repository reasoning
- task handoff preparation

Do not use it for small surgical edits when Aider can do the job faster.

## Scalpel - Aider

Aider is the focused code-editing tool.

Use it for:

- targeted bug fixes
- small feature implementation
- refactors with limited blast radius
- patch review and iteration

Aider should operate inside one active project mounted read-write.

## Lens - Continue

Continue is the IDE assistance layer.

Use it for:

- inline code suggestions
- local chat inside VS Code
- quick explanations
- developer-in-the-loop editing

Continue is configured outside Docker as a VS Code extension, pointed at Guardian.

## Operator - Agent Zero

Agent Zero is the sandboxed task runner for heavier system work.

Current status: experimental and parked as a primary interactive coding agent. Its UI can leave long-running local reasoning calls looking idle while GPUs are busy, so do not use it as the default cockpit.

Use it for:

- installing tool dependencies inside a container
- reproducing environment issues
- running scripts and diagnostics
- temporary automation experiments

Agent Zero must not get broad host access by default.

## Gatekeeper - Guardian

Guardian is the OpenAI-compatible broker for local model access.

KyberM0nk should only call Guardian. It must not start or control raw `llama-server` instances.

## Engine - llama.cpp

`llama-server` is the inference backend. It is managed by Guardian and remains outside KyberM0nk.
