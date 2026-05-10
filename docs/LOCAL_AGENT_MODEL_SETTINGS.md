# Local Agent Model Settings

KyberM0nk routes local coding agents through Guardian alias `qwen3-35b-reasoning-agent` by default. The current benchmark evidence shows that the machine can handle large contexts, but the best day-to-day agent settings are not the maximum possible settings.

The generic deep alias `qwen3-35b-uncensored` stays available for explicit max-reasoning runs. Daily local-agent tools use `qwen3-35b-reasoning-agent`: Qwen reasoning stays enabled, but Guardian caps the reasoning budget so frameworks cannot burn minutes in invisible deep-think loops. Agent Zero currently uses `gemma4-26b-agent` because the 26B Gemma4 route is responsive enough for default NewNexus work. The 31B uncensored route remains available as `gemma4-31b-uncensored-max-agent` for explicit quality tests.

## Current Recommendation

| Tool | Context | History/Input Share | Normal Output | Timeout | Reasoning Policy |
|------|---------|---------------------|---------------|---------|------------------|
| OpenCode / interpreter | `65536` | tool-managed | `4096` | wrapper/runtime default | Guardian bounded reasoning alias |
| Agent Zero chat | `65536` | `ctx_history: 0.35` | `1536` | `240s` | Guardian `gemma4-26b-agent` loop-safe Gemma4 route |
| Agent Zero utility | `32768` | `ctx_input: 0.35` | `1024` | `180s` | Guardian `gemma4-26b-agent` loop-safe Gemma4 route |
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
- Agent Zero can appear to hang while local models emit hidden reasoning. Keep reasoning enabled for the user's requested max-reasoning mode, but prevent loops with tool guardrails, anti-repeat sampler settings, and output caps.
- Agent Zero can also repeat visible JSON thoughts when old tool guidance fails. Keep its default history and output caps lower than OpenCode so stale chat context cannot dominate a full response.
- Reasoning is still useful for local coding agents, but it needs a budget. Use `qwen3-35b-reasoning-agent` for normal local agent work and reserve `qwen3-35b-uncensored` for explicit deep/manual runs.

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
DEFAULT_MODEL=qwen3-35b-reasoning-agent
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

The configured Agent Zero Guardian model name is currently `gemma4-26b-agent`. This keeps AZ on the faster Gemma4 26B route for default NewNexus work. Use `gemma4-31b-uncensored-max-agent` only for explicit 31B quality/tuning tests until it has a proven sampler/context profile that is not too slow for routine AZ loops.

## Benchmark Artifacts

Use these scripts to keep recommendations evidence-based:

```bash
python3 scripts/benchmark_guardian_context.py --order decision --preset max --output-sizes 32,1024,4096,8192 --tasks all --thinking-modes both --context-limit 131072 --skip-over-context --timeout 1200
python3 scripts/render_benchmark_trends.py logs/guardian-context-benchmarks/<run>.csv
```

The decision order gives a fast ballpark by testing spread-out context sizes and practical decode caps before filling in less urgent combinations.