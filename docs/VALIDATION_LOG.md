# Validation Log

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