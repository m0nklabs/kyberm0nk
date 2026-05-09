# Validation Log


## 2026-05-09 - Agent Zero Gemma4 Vision Route

Scope:

- Enable Agent Zero's Gemma4 chat route to advertise vision support.
- Keep Agent Zero on Guardian alias `gemma4-agent`, with Guardian carrying the Gemma4 multimodal projector.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Guardian direct vision smoke | Passed | `gemma4-agent` loaded with `--mmproj` and identified a generated red PNG as `red` |
| Agent Zero runtime config | Passed | `/opt/agent-zero/usr/plugins/_model_config/config.json` reports `chat_model.vision == true` |
| Agent Zero wrapper vision smoke | Passed | AZ `get_chat_model` / `LiteLLMChatWrapper` accepted a LangChain `HumanMessage` with `image_url` content and returned `red` |
| Windows executor regression smoke | Passed | `scripts/test_windows_unreal_ssh.sh` still reaches `14700K` from host and sandbox after the sandbox cleanup |
| Clipboard upload path smoke | Passed | `/a0/usr/uploads` now resolves to `/opt/agent-zero/usr/uploads`, where pasted clipboard images are stored |
| Clipboard image conversion smoke | Passed | A real pasted `/a0/usr/uploads/clipboard-*.png` file converted to a `data:image/png;base64,...` URL and produced a Gemma4 vision response through AZ's wrapper |

Operational note:

- `agent_zero_up.sh` previously used `docker compose up -d sandbox`, which allowed Compose to recreate the sandbox when service config drifted. It now starts an existing container directly and only creates a container with `--no-build` when none exists.
- Agent Zero's UI records pasted files as `/a0/usr/uploads/...`, while the container stores them under `/opt/agent-zero/usr/uploads/...`; the startup script now maintains a symlink for that path.
- Agent Zero's upstream `vision_load` passes local file paths as `image_url.url`; the Kyber patch converts those files to data URLs because Guardian/llama.cpp cannot read container-local paths from an OpenAI-compatible request.

## 2026-05-09 - Agent Zero Gemma4 Compatibility Smoke

Scope:

- Add Guardian alias `gemma4-agent` for a 65k-context Gemma4 26B A4B profile.
- Temporarily route Agent Zero chat and utility models to `gemma4-agent`.
- Verify direct Guardian inference, Agent Zero's LiteLLM wrapper, and the real Agent Zero UI/API message path.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Guardian YAML and AZ JSON syntax | Passed | Parsed `config/models.yaml` and `configs/agent-zero/model_config.json` successfully |
| Direct Guardian smoke | Passed | `gemma4-agent` returned `GEMMA4_OK` at about 40 tokens/sec decode |
| Agent Zero model-wrapper smoke | Passed | AZ LiteLLM route returned `AZ_GEMMA4_OK` |
| Agent Zero UI/API message smoke | Passed with observation | UI/API accepted a message and logged a `response` tool payload with `AZ_UI_GEMMA4_OK` |
| Whole-plan tool-loop observation | In progress | AZ created `/opt/agent-zero/usr/workdir/rimworld_sim/entities.py` through a subordinate/tool loop |
| GPU cleanup | Passed | Guardian `/admin/unload` stopped `llama-server`; only Frigate remained on GPU0 after cleanup |

Operational note:

- The UI/API message request exceeded a 20-second client timeout during first-run VectorDB/knowledge initialization, but Agent Zero continued and logged the correct response payload.
- Agent Zero logged `Memory consolidation timeout for area fragments` during the longer run, then continued and wrote the file. Treat this as AZ framework overhead to watch, not a Gemma4 inference failure.
- Keep the run bounded and monitor GPU status while deciding whether AZ is viable with Gemma4.

## 2026-05-08 - Balanced Local Agent Settings

Scope:

- Apply benchmark-based balanced model settings to OpenCode and Agent Zero.
- Document the server-wide policy in the shared MARK1/global Copilot config.
- Validate that both tools still route through Guardian and load the intended settings.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Agent Zero JSON syntax | Passed | `python3 -m json.tool configs/agent-zero/model_config.json` |
| Shell syntax | Passed | `bash -n scripts/opencode.sh scripts/agent_zero_up.sh scripts/agent_zero_down.sh` |
| Python helper syntax | Passed | `python3 -m py_compile scripts/benchmark_guardian_context.py scripts/render_benchmark_trends.py` |
| VS Code diagnostics | Passed | No errors for benchmark helper scripts or Agent Zero JSON |
| Docker Compose config | Passed with warning | Compose warns that top-level `version` is obsolete |
| OpenCode smoke test | Passed | Wrapper used `context=65536`, `max_tokens=4096`, `temperature=0.2`; model replied `KYBERM0NK_OPENCODE_OK` |
| Agent Zero startup | Passed | `/api/health` returned healthy JSON after restart |
| Agent Zero loaded config | Passed | Container config shows chat `65536/0.55/420s`, utility `32768/0.45/240s` |

Operational note:

- The long Qwen3.6 matrix benchmark was paused before final tool tests.
- Persisted benchmark rows remain in `logs/guardian-context-benchmarks/` and can be continued with `--resume`.
- A previous benchmark interruption left an orphaned `llama-server`; Guardian was reset before smoke tests.