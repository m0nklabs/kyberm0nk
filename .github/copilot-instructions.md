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

## Repository Hygiene

- Root should stay clean: README, CHANGELOG, standard config/manifests only.
- Put durable planning and design notes in `docs/`.
- Put reusable helper scripts in `scripts/`.
- Put tool-specific config under `configs/<tool>/`.
- Update `docs/TODO_LIST.md` when adding or completing work.

## Current Primary Model Target

Use Guardian alias `qwen3-35b-uncensored` as the initial deep model target unless the operator changes Guardian policy.
