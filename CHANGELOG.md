# Changelog

## 2026-05-08

- **Agent Zero non-thinking Guardian route:**
  - Switched Agent Zero chat and utility models to Guardian alias `qwen3-35b-uncensored-agent`.
  - Added hard LiteLLM output caps in `configs/agent-zero/model_config.json` (`4096` chat tokens, `2048` utility tokens).
  - Documented why Agent Zero should use a non-thinking Qwen profile for routine tool work: Agent Zero's own installation guide warns reasoning/thinking can increase latency, and Qwen's llama.cpp guide requires a custom non-thinking chat template for the hard switch.

- **Guardian context benchmark suite:**
  - Replaced the ad-hoc 32k context test with `scripts/benchmark_guardian_context.py`.
  - Added context-size presets, JSONL/CSV output, `nvidia-smi` GPU sampling, and timeout reset protection for runaway `llama-server` requests.
  - Added a `max` preset for near-limit tests up to the current Qwen `131072` context setting.
  - Added a `reasoning-stress` task mode for comparing context prefill against long reasoning/decode behavior.
  - Added a `long-decode` task mode to force high completion-token benchmarks.
  - Expanded the benchmark into a full matrix suite across input sizes, completion caps, task modes, and thinking modes.
  - Added context budget metadata and estimated content-vs-reasoning token split columns.
  - Persist benchmark JSONL/CSV after every matrix case so long runs keep partial results if interrupted.
  - Added `--resume` support for continuing interrupted matrix runs from existing JSONL output.
  - Added `--order decision` and `--order shuffle` so runs can gather early tuning signal or spread bias instead of always walking the matrix sequentially.
  - Added `scripts/render_benchmark_trends.py` to turn benchmark CSV files into standalone trend reports.
  - Applied benchmark-based balanced defaults to Agent Zero and OpenCode.
  - Documented the local coding-agent model budget in `docs/LOCAL_AGENT_MODEL_SETTINGS.md`.
  - Added `docs/VALIDATION_LOG.md` with final validation results for the tuned OpenCode and Agent Zero settings.
  - Documented the workflow in `docs/GUARDIAN_CONTEXT_BENCHMARKS.md`.
  - Removed a hardcoded Guardian API key from `scripts/test_aider_headless.sh`.

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
