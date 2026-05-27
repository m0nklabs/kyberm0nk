# Guardian Context Benchmarks

This benchmark measures how the current Guardian model behaves as input context grows. It is meant to answer practical questions like whether Agent Zero is slow because of model/context size, Guardian queue behavior, or runaway inference after client timeouts.

## Script

Run from the KyberM0nk repository root:

```bash
python3 scripts/benchmark_guardian_context.py --preset smoke
```

The script uses only the Python standard library. It reads `KYBERM0NK_GUARDIAN_API_KEY` and `DEFAULT_MODEL` from `.env`, calls Guardian's OpenAI-compatible `/v1/chat/completions` endpoint, samples `nvidia-smi`, and writes results to `logs/guardian-context-benchmarks/`.

Each target context size uses deterministic but size-specific synthetic text. That avoids accidentally benchmarking a warm prefix/KV cache instead of prompt-processing cost.

By default the script sends `chat_template_kwargs.enable_thinking=false` so Qwen-style reasoning does not consume the output budget. Use `--enable-thinking` when you want to mimic Agent Zero's current behavior more closely.

The script can run one benchmark or a full matrix. Matrix dimensions are:

- Input context sizes: `--sizes` or `--preset`.
- Completion caps: `--output-sizes`, `--output-preset`, or legacy `--max-output-tokens`.
- Task type: `--task` or `--tasks`.
- Thinking mode: `--thinking-modes disabled|enabled|both`.

## Presets

| Preset | Target Context Sizes |
|--------|----------------------|
| `smoke` | `128,256` |
| `ramp` | `1024,2048,4096,8192,12288,16384` |
| `agent-zero` | `4096,8192,12288,16384,24576,32768` |
| `full` | `1024,2048,4096,8192,12288,16384,24576,32768` |
| `max` | `32768,49152,65536,81920,98304,114688,122880,126976,131072` |

Output presets:

| Preset | Completion Caps |
|--------|-----------------|
| `tiny` | `32,128` |
| `standard` | `32,256,1024,2048,4096,8192` |
| `decode` | `512,2048,4096,8192,16384` |
| `max` | `32,1024,4096,8192,16384,32768` |

You can override presets:

```bash
python3 scripts/benchmark_guardian_context.py --sizes 4096,8192,12288 --timeout 600
```

The default task is a short marker recall benchmark. To stress long reasoning/decode behavior, use:

```bash
python3 scripts/benchmark_guardian_context.py --sizes 32768 --task reasoning-stress --enable-thinking --max-output-tokens 2048 --timeout 600
```

To force a high completion-token run instead of allowing the model to stop naturally, use:

```bash
python3 scripts/benchmark_guardian_context.py --sizes 32768 --task long-decode --enable-thinking --max-output-tokens 8192 --timeout 1800
```

Full matrix example for the current Qwen configuration:

```bash
python3 scripts/benchmark_guardian_context.py \
	--preset max \
	--output-preset standard \
	--tasks marker,reasoning-stress,long-decode \
	--thinking-modes both \
	--context-limit 131072 \
	--skip-over-context \
	--timeout 1800 \
	--run-name qwen_full_matrix
```

Plan a matrix before running it:

```bash
python3 scripts/benchmark_guardian_context.py \
	--preset max \
	--output-preset standard \
	--tasks all \
	--thinking-modes both \
	--context-limit 131072 \
	--skip-over-context \
	--plan-only
```

When you need a fast ballpark instead of a complete table, use decision ordering. It tests prefill markers, practical long-decode caps, and reasoning stress points across spread-out context sizes before filling in less urgent combinations:

```bash
python3 scripts/benchmark_guardian_context.py \
	--preset max \
	--output-sizes 32,1024,4096,8192 \
	--tasks all \
	--thinking-modes both \
	--context-limit 131072 \
	--skip-over-context \
	--order decision \
	--timeout 1200 \
	--run-name qwen_decision_ballpark
```

Use `--order shuffle --seed 1234` when you want to spread thermal/cache bias across the matrix.

Example for a larger-context model such as `gemma4-heretic-deep`:

```bash
python3 scripts/benchmark_guardian_context.py \
	--model gemma4-heretic-deep \
	--sizes 32768,65536,131072,180224,196608,212992 \
	--output-sizes 32,1024,4096,8192,16384 \
	--tasks marker,long-decode \
	--thinking-modes both \
	--context-limit 216064 \
	--skip-over-context \
	--timeout 2400 \
	--run-name gemma4_deep_matrix
```

Agent Zero-style run with reasoning left enabled:

```bash
python3 scripts/benchmark_guardian_context.py --preset agent-zero --timeout 900 --enable-thinking
```

Near-limit run for the current `qwen3-35b-uncensored` configuration:

```bash
python3 scripts/benchmark_guardian_context.py --preset max --timeout 1200
```

The current Qwen alias is configured in Guardian with `context: 131072`. The final `131072` target is expected to be near or just over the real request limit once chat-template/system-message overhead is included.

## Safety Behavior

By default, a timed-out request triggers a best-effort local reset:

```text
sudo pkill -9 llama-server
sudo systemctl restart llama-guardian
```

This prevents the exact failure mode where the client gives up but `llama-server` keeps burning GPU in the background. Disable this only when intentionally debugging Guardian cancellation behavior:

```bash
python3 scripts/benchmark_guardian_context.py --preset full --no-reset-on-timeout
```

## Output

Each run writes:

- JSONL with full result records and per-GPU summaries.
- CSV with a compact table for plotting or spreadsheet comparison.

The files are rewritten after every matrix case, so partial data survives if a long run is interrupted.

Render a trend report from any benchmark CSV:

```bash
python3 scripts/render_benchmark_trends.py \
	logs/guardian-context-benchmarks/qwen_full_matrix.csv
```

The report includes prompt-prefill latency, long-decode elapsed time, long-decode tokens/sec, and a risk map for long-decode failures.

Resume an interrupted matrix by reusing the same run name and adding `--resume`:

```bash
python3 scripts/benchmark_guardian_context.py \
	--preset max \
	--output-preset max \
	--tasks all \
	--thinking-modes both \
	--context-limit 131072 \
	--skip-over-context \
	--resume \
	--run-name qwen_full_matrix
```

Important columns:

- `target_context_tokens`: requested synthetic context size.
- `max_output_tokens`: requested completion cap.
- `task`: benchmark task (`marker`, `reasoning-stress`, or `long-decode`).
- `thinking_mode`: `disabled` or `enabled`.
- `context_limit_tokens`, `requested_total_budget_tokens`, and `budget_status`: matrix budget metadata.
- `usage_prompt_tokens`: server-reported prompt token count when Guardian/llama.cpp returns usage metadata.
- `usage_completion_tokens`: server-reported generated token count.
- `estimated_content_tokens` and `estimated_reasoning_tokens`: approximate split based on response character ratios. The OpenAI-compatible API reports total completion tokens, not a perfect content-vs-reasoning token split.
- `remaining_context_after_prompt_tokens` and `remaining_context_after_completion_tokens`: remaining tokens when `--context-limit` is supplied.
- `elapsed_seconds`: wall-clock request duration.
- `status`: `ok`, `timeout`, `http-error`, `url-error`, or `error`.
- `finish_reason`, `content_chars`, `reasoning_chars`, and `marker_found`: useful for spotting reasoning-mode runs that spend the output budget before producing normal answer content.
- `max_gpu_utilization_pct`: highest sampled GPU utilization.
- `max_total_power_w`: highest combined GPU power draw.
- `max_total_memory_mib`: highest combined GPU memory use.

## Recommended Test Flow

1. Run `--preset smoke` to confirm Guardian/auth/config are correct.
2. Run `--preset ramp` for practical Agent Zero tuning.
3. Run `--preset agent-zero --timeout 900` only when you explicitly want to test large-context behavior.
4. If a timeout happens, inspect the CSV and verify `nvidia-smi` settles before starting another run.
5. Use `--plan-only` before large matrix runs; matrix size grows quickly.
