# Changelog

## 2026-05-08

- **Agent Zero Architecture overhaul:**
  - Removed brittle shell `sed` patching from `agent_zero_up.sh`.
  - Introduced clean, read-only volume-mounted patches (`configs/agent-zero/patches/*`).
  - Integrated a dedicated `searxng/searxng` container via `docker-compose.yml` to resolve internal localhost hardcode conflicts when Agent Zero probes for search APIs.
  - Hardened Agent Zero's heavy generation tasks by moving LLM invocation timeouts explicitly into `configs/agent-zero/model_config.json` with a generous 5-minute timeout window (`300.0s`), drastically mitigating `APITimeoutError`s during background context compaction steps with the Qwen3-35B model.

## 2026-05-06

- Initialized KyberM0nk as a documentation-first local agentic coding cockpit.
- Documented the Guardian-outside-Docker and agent-tools-inside-Docker architecture.
- Added initial role definitions, security model, workspace setup notes, and roadmap.

- Expanded `ROADMAP.md` and `TODO_LIST.md` with explicit tool hierarchy mapping (Motor, General, Executioner, Scalpel, IDE-Glasses) based on user's structural masterplan.
- Added host-level Guardian proxy connection from Docker containers.
- Added Aider (Scalpel) integration, successfully tested Guardian connection and volume writes.
- Added OpenCode (General) integration, using open-interpreter, configured with specific system prompts.
- Added Agent Zero (Executioner) integration, customized the Dockerfile to pre-cache compilation steps for PyPI dependencies avoiding Cython build timeouts.
- Set up and documented Continue (IDE-Glasses) endpoint configuration with generated API key (`config.yaml`).
- **Agent Zero wired to Guardian (end-to-end working).**
  - Sandbox base image upgraded to `python:3.12-slim` (AZ uses PEP 695 `type` syntax).
  - Pinned `httpx<0.28` in Dockerfile: openai 1.42 / litellm 1.44 still pass the removed `proxies` kwarg, breaking all chat completions otherwise.
  - User override is `configs/agent-zero/model_config.json` (NOT yaml — AZ's plugin system reads `config.json` for user overrides; yaml is only for bundled defaults).
  - `chat_model` and `utility_model` route through `provider: other` (generic OpenAI-compatible) → `http://host.docker.internal:11434/v1` → Guardian alias `qwen3-35b-uncensored`.
  - Compose env: `OTHER_API_KEY=${GUARDIAN_API_KEY}`, port `127.0.0.1:50001:50001`.
  - `scripts/agent_zero_up.sh` copies the JSON into `/opt/agent-zero/usr/plugins/_model_config/config.json` on each launch.
  - Verified: `models.get_chat_model(...).ainvoke(...)` returns `'OK'` from Guardian. UI live at http://127.0.0.1:50001.
