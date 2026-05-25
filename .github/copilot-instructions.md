# KyberM0nk Copilot Instructions

## Project Purpose

KyberM0nk is a local agentic coding cockpit. It coordinates coding tools around the existing Guardian proxy and does not own the inference backend.

## Hard Rules

- Keep Guardian and `llama-server` outside this repository and outside Docker images.
- Never spawn a standalone `llama-server` from this project.
- Never access Guardian backend port `11440` directly.
- Use Guardian proxy port `11434` and the OpenAI-compatible `/v1` API.
- Do not hardcode secrets. Use `.env` and document required variables in `.env.example`.
- Mount the active project read-write only when explicitly selected.
- Mount reference repositories read-only by default.
- Do not mount the Docker socket unless a task explicitly requires it and the risk is documented.
- Project documentation, code comments, and commits must be in English.


## Framework Stewardship

- KyberM0nk exists to manage agent frameworks themselves: runtime roots, wrappers, prompts, tool policy, schedulers, MCP wiring, safety rails, observability, and autonomy settings.
- Do not use KyberM0nk sessions to do the downstream domain work of those frameworks by hand. In particular, when working on Hermes from Kyber, focus on making Hermes more autonomous and reliable rather than manually doing Hermes' repo triage, review, or operating work.
- Validation is allowed: run bounded framework-level tests, dry-runs, and scheduler executions to confirm Hermes behavior. But after the framework path is healthy, let Hermes do its own recurring work.
- When a change drifts from framework management into application/domain execution, stop and move that work back into the framework's own autonomous loop, prompt, skill, cron, kanban, or runtime policy.
## Repository Hygiene

- Root should stay clean: README, CHANGELOG, standard config/manifests only.
- Put durable planning and design notes in `docs/`.
- Put reusable helper scripts in `scripts/`.
- Put tool-specific config under `configs/<tool>/`.
- Update `docs/TODO_LIST.md` when adding or completing work.

## Current Primary Model Target

Use Guardian alias `qwen3-35b-uncensored` as the initial deep model target unless the operator changes Guardian policy.

## Local Agent Model Defaults

- Use benchmark-based balanced defaults for local coding agents; do not default to maximum context plus maximum output.
- OpenCode default profile: `65536` context, `4096` max tokens, `0.2` temperature.
- Agent Zero default profile: `65536` chat context with `ctx_history: 0.55`; utility model stays at `32768` with `ctx_input: 0.45`.
- Avoid `32768` output-token caps for normal coding-agent work; benchmark data shows long-decode failures around the 600-second boundary.
- Prefer staged context gathering, summaries, and durable handoff notes over dumping full repositories into a single prompt.
- See `docs/LOCAL_AGENT_MODEL_SETTINGS.md` before changing tool model budgets.
