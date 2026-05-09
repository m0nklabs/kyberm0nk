# Local Agent Model Settings

KyberM0nk routes local coding agents through Guardian alias `qwen3-35b-uncensored-agent`. The current benchmark evidence shows that the machine can handle large contexts, but the best day-to-day agent settings are not the maximum possible settings.

The generic deep alias `qwen3-35b-uncensored` stays available for explicit reasoning runs. Agent tools use the `-agent` alias because Agent Zero's own installation guide warns that reasoning/thinking can increase latency and recommends disabling it with provider-specific parameters when a model supports it. Qwen's llama.cpp documentation says the hard `enable_thinking=False` switch is not exposed directly in llama.cpp and recommends a custom non-thinking chat template; Guardian implements that workaround in `config/qwen3_nonthinking.jinja`.

## Current Recommendation

| Tool | Context | History/Input Share | Normal Output | Timeout | Reasoning Policy |
|------|---------|---------------------|---------------|---------|------------------|
| OpenCode | `65536` | tool-managed | `4096` | wrapper/runtime default | Use targeted planning; avoid huge dumps |
| Agent Zero chat | `65536` | `ctx_history: 0.55` | `4096` | `420s` | Guardian non-thinking alias |
| Agent Zero utility | `32768` | `ctx_input: 0.45` | `2048` | `240s` | Guardian non-thinking alias |
| Deep manual benchmark mode | `98304` or higher | task-specific | `8192` max | `900s+` | Only for explicit deep-analysis runs |

Do not use `131072` context plus `32768` output as a default agent setting. That shape is useful for stress tests, but too slow and fragile for normal coding work.

## Why These Values

The Qwen3.6 benchmark matrix showed:

- `32768` to `65536` prompt tokens are practical for coding-agent work.
- `81920` prompt tokens still works, but prompt prefill becomes noticeably heavier.
- Long-decode requests with `32768` output cap repeatedly hit HTTP 500 around the 600-second boundary.
- `4096` output is a good normal cap for planning and code explanations.
- `8192` output is a reasonable explicit deep-task cap.
- Reasoning output may appear in `reasoning_content` instead of normal `content`; tool-facing agents should avoid relying on huge hidden reasoning for final actionable output.
- Agent Zero can appear to hang while Qwen emits hidden reasoning. The `-agent` alias uses Qwen's non-thinking template so output is visible quickly and bounded by request-level `max_tokens`.

## Operational Pattern

The local stack should imitate Copilot-style context usage by using retrieval and staged context, not by blindly stuffing the full repository into every prompt.

Preferred flow:

1. Read the smallest relevant files first.
2. Summarize findings before loading more context.
3. Keep tool output concise and structured.
4. Store durable conclusions in docs, TODO files, or handoff notes.
5. Escalate to larger context only when the task needs it.

## OpenCode Defaults

OpenCode is wired through `scripts/opencode.sh` with these `.env` defaults:

```text
OPENCODE_CONTEXT_WINDOW=65536
OPENCODE_MAX_TOKENS=4096
OPENCODE_TEMPERATURE=0.2
OPENCODE_MAX_OUTPUT_CHARS=20000
```

Override them per run in `.env` or the shell when intentionally testing a different profile.

## Agent Zero Defaults

Agent Zero reads `configs/agent-zero/model_config.json` through its `_model_config` plugin.

The supported and configured fields are:

- `ctx_length` for the model context window.
- `ctx_history` for chat history share.
- `ctx_input` for utility model input share.
- `kwargs.timeout` for request timeout.
- `kwargs.max_tokens` for hard output caps passed through LiteLLM.

The configured Guardian model name is `qwen3-35b-uncensored-agent`, not the unrestricted deep-reasoning alias. Keep `qwen3-35b-uncensored` for explicit deep/manual runs where hidden reasoning is worth the latency.

## Benchmark Artifacts

Use these scripts to keep recommendations evidence-based:

```bash
python3 scripts/benchmark_guardian_context.py --order decision --preset max --output-sizes 32,1024,4096,8192 --tasks all --thinking-modes both --context-limit 131072 --skip-over-context --timeout 1200
python3 scripts/render_benchmark_trends.py logs/guardian-context-benchmarks/<run>.csv
```

The decision order gives a fast ballpark by testing spread-out context sizes and practical decode caps before filling in less urgent combinations.