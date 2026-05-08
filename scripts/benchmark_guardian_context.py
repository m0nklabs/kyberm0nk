#!/usr/bin/env python3
"""Benchmark Guardian chat latency across multiple context sizes."""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any


PlanItem = tuple[int, int, str, bool]


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "guardian-context-benchmarks"
DEFAULT_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_MODEL = "qwen3-35b-uncensored"
PRESETS = {
    "smoke": [128, 256],
    "ramp": [1024, 2048, 4096, 8192, 12288, 16384],
    "agent-zero": [4096, 8192, 12288, 16384, 24576, 32768],
    "full": [1024, 2048, 4096, 8192, 12288, 16384, 24576, 32768],
    "max": [32768, 49152, 65536, 81920, 98304, 114688, 122880, 126976, 131072],
}
TASKS = ("marker", "reasoning-stress", "long-decode")
OUTPUT_PRESETS = {
    "tiny": [32, 128],
    "standard": [32, 256, 1024, 2048, 4096, 8192],
    "decode": [512, 2048, 4096, 8192, 16384],
    "max": [32, 1024, 4096, 8192, 16384, 32768],
}
COMMON_WORDS = [
    "system",
    "local",
    "agent",
    "model",
    "context",
    "memory",
    "project",
    "signal",
    "result",
    "token",
    "window",
    "prompt",
    "queue",
    "trace",
    "sample",
    "runtime",
    "guardian",
    "benchmark",
    "measure",
    "stable",
    "response",
    "kernel",
    "stream",
    "control",
    "latency",
    "throughput",
    "worker",
    "server",
    "request",
    "finish",
    "health",
    "reason",
]


@dataclass(frozen=True)
class GpuSample:
    """Single nvidia-smi sample."""

    timestamp: float
    gpu_index: int
    utilization_pct: float
    power_w: float
    memory_used_mib: float
    temperature_c: float


def load_dotenv(path: Path) -> dict[str, str]:
    """Load simple KEY=VALUE pairs from a dotenv file without external deps."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_sizes(raw_sizes: str | None, preset: str) -> list[int]:
    """Parse an explicit comma-separated size list or named preset."""
    if raw_sizes:
        sizes = [int(item.strip()) for item in raw_sizes.split(",") if item.strip()]
    else:
        sizes = PRESETS[preset]

    if not sizes:
        raise ValueError("at least one context size is required")
    if any(size <= 0 for size in sizes):
        raise ValueError("context sizes must be positive integers")
    return sizes


def parse_int_list(raw_values: str, label: str) -> list[int]:
    """Parse comma-separated positive integers."""
    values = [int(item.strip()) for item in raw_values.split(",") if item.strip()]
    if not values:
        raise ValueError(f"at least one {label} value is required")
    if any(value <= 0 for value in values):
        raise ValueError(f"{label} values must be positive integers")
    return values


def parse_output_sizes(args: argparse.Namespace) -> list[int]:
    """Parse output token caps from explicit values, preset, or legacy single cap."""
    if args.output_sizes:
        return parse_int_list(args.output_sizes, "output size")
    if args.output_preset:
        return OUTPUT_PRESETS[args.output_preset]
    return [args.max_output_tokens]


def parse_tasks(raw_tasks: str | None, fallback_task: str) -> list[str]:
    """Parse one or more benchmark tasks."""
    if not raw_tasks:
        return [fallback_task]
    if raw_tasks == "all":
        return list(TASKS)

    tasks = [item.strip() for item in raw_tasks.split(",") if item.strip()]
    unknown_tasks = sorted(set(tasks) - set(TASKS))
    if unknown_tasks:
        raise ValueError(f"unknown task(s): {', '.join(unknown_tasks)}")
    return tasks


def parse_thinking_modes(args: argparse.Namespace) -> list[bool]:
    """Return disable_thinking values for the requested thinking modes."""
    if args.thinking_modes == "disabled":
        return [True]
    if args.thinking_modes == "enabled":
        return [False]
    if args.thinking_modes == "both":
        return [True, False]
    return [args.disable_thinking]


def thinking_label(disable_thinking: bool) -> str:
    """Human-readable thinking mode label."""
    return "disabled" if disable_thinking else "enabled"


def build_context(target_tokens: int, marker: str, salt: str) -> str:
    """Build deterministic benchmark context with a marker near the end."""
    salt_marker = f"salt {salt} size {target_tokens} marker {marker}"
    words: list[str] = salt_marker.split()
    salt_value = sum(ord(character) for character in salt) + (target_tokens * 17)
    for index in range(max(0, target_tokens - len(words) - 12)):
        word_index = ((index * 7) + salt_value) % len(COMMON_WORDS)
        words.append(COMMON_WORDS[word_index])

    words.extend(
        [
            "final",
            "marker",
            "for",
            "this",
            "benchmark",
            "run",
            "is",
            marker,
            "repeat",
            "only",
            "that",
            "marker",
        ]
    )
    return " ".join(words)


def build_payload(
    model: str,
    target_tokens: int,
    max_output_tokens: int,
    temperature: float,
    disable_thinking: bool,
    salt: str,
    task: str,
) -> dict[str, Any]:
    """Build a small-output chat-completions request with large input context."""
    marker = f"KYBERM0NK_CONTEXT_{target_tokens}"
    context = build_context(target_tokens, marker, salt)
    if task == "long-decode":
        system_content = (
            "You are running a long decode benchmark. The benchmark needs a long completion. "
            "Do not summarize. Do not stop early. Continue until the generation limit stops you."
        )
        user_content = (
            f"Benchmark context begins.\n{context}\nBenchmark context ends.\n\n"
            "Write a very long numbered operations runbook for diagnosing local LLM agent failures. "
            "Each item must be one sentence and must include a distinct counter, subsystem name, "
            "observable signal, failure mode, and mitigation. Keep writing numbered items continuously. "
            "Do not conclude. Do not include a summary. "
            f"If you reach the end naturally, write this exact marker: {marker}"
        )
    elif task == "reasoning-stress":
        system_content = (
            "You are running a reasoning stress benchmark. Use careful internal reasoning if available. "
            "The benchmark measures long reasoning/decode behavior, not answer quality."
        )
        user_content = (
            f"Benchmark context begins.\n{context}\nBenchmark context ends.\n\n"
            "Analyze this operations incident in detail: an agent sends large prompts through a Guardian "
            "proxy to llama.cpp, the client can disconnect, GPU load can continue, and queue state can drift. "
            "Compare at least five root-cause hypotheses, reject weak ones, propose instrumentation, "
            "define safety timeouts, and produce a final prioritized fix plan. "
            f"End the final answer with this exact marker: {marker}"
        )
    else:
        system_content = (
            "You are running a latency benchmark. Do not solve a task. "
            "Do not explain. Return exactly the requested marker."
        )
        user_content = (
            f"Benchmark context begins.\n{context}\nBenchmark context ends.\n"
            f"Return exactly this marker and nothing else: {marker}"
        )

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "max_tokens": max_output_tokens,
        "temperature": temperature,
    }
    if disable_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    return payload


def estimate_completion_split(
    content_chars: int,
    reasoning_chars: int,
    completion_tokens: int | None,
) -> tuple[int | None, int | None]:
    """Estimate content/reasoning token split from character ratios."""
    if completion_tokens is None:
        return None, None

    total_chars = content_chars + reasoning_chars
    if total_chars <= 0:
        return 0, 0

    reasoning_tokens = round(completion_tokens * (reasoning_chars / total_chars))
    content_tokens = completion_tokens - reasoning_tokens
    return content_tokens, reasoning_tokens


def requested_budget_status(
    context_limit: int | None,
    target_tokens: int,
    max_output_tokens: int,
    overhead_tokens: int,
) -> str:
    """Classify approximate pre-request budget fit."""
    if context_limit is None:
        return "unknown"
    requested_budget = target_tokens + max_output_tokens + overhead_tokens
    return "fits" if requested_budget <= context_limit else "over-budget"


def build_skipped_result(
    args: argparse.Namespace,
    target_tokens: int,
    max_output_tokens: int,
    task: str,
    disable_thinking: bool,
    reason: str,
) -> dict[str, Any]:
    """Build a result row for an intentionally skipped matrix combo."""
    return {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "target_context_tokens": target_tokens,
        "task": task,
        "thinking_mode": thinking_label(disable_thinking),
        "thinking_enabled": not disable_thinking,
        "max_output_tokens": max_output_tokens,
        "context_limit_tokens": args.context_limit,
        "requested_total_budget_tokens": target_tokens + max_output_tokens + args.overhead_tokens,
        "budget_status": requested_budget_status(
            args.context_limit, target_tokens, max_output_tokens, args.overhead_tokens
        ),
        "payload_bytes": None,
        "timeout_seconds": args.timeout,
        "elapsed_seconds": 0,
        "status": "skipped",
        "http_status": None,
        "response_preview": "",
        "response_chars": 0,
        "content_chars": 0,
        "reasoning_chars": 0,
        "finish_reason": "",
        "marker_found": False,
        "usage_prompt_tokens": None,
        "usage_completion_tokens": None,
        "usage_total_tokens": None,
        "estimated_content_tokens": None,
        "estimated_reasoning_tokens": None,
        "remaining_context_after_prompt_tokens": None,
        "remaining_context_after_completion_tokens": None,
        "error": reason,
        "reset_result": "not-needed",
        "gpu": summarize_gpu([]),
    }


class GpuSampler:
    """Poll nvidia-smi while a benchmark request is in flight."""

    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds = interval_seconds
        self.samples: list[GpuSample] = []
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.available = shutil.which("nvidia-smi") is not None

    def __enter__(self) -> "GpuSampler":
        if self.available:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.interval_seconds + 2)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self.samples.extend(read_gpu_samples())
            self._stop_event.wait(self.interval_seconds)


def read_gpu_samples() -> list[GpuSample]:
    """Read one GPU telemetry snapshot from nvidia-smi."""
    command = [
        "nvidia-smi",
        "--query-gpu=index,utilization.gpu,power.draw,memory.used,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=5)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []

    timestamp = time.time()
    samples: list[GpuSample] = []
    for line in completed.stdout.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 5:
            continue
        try:
            samples.append(
                GpuSample(
                    timestamp=timestamp,
                    gpu_index=int(parts[0]),
                    utilization_pct=float(parts[1]),
                    power_w=float(parts[2]),
                    memory_used_mib=float(parts[3]),
                    temperature_c=float(parts[4]),
                )
            )
        except ValueError:
            continue
    return samples


def summarize_gpu(samples: list[GpuSample]) -> dict[str, Any]:
    """Summarize raw GPU samples for CSV/JSON output."""
    if not samples:
        return {
            "sample_count": 0,
            "avg_utilization_pct": None,
            "max_utilization_pct": None,
            "avg_total_power_w": None,
            "max_total_power_w": None,
            "max_total_memory_mib": None,
            "max_temperature_c": None,
            "per_gpu": {},
        }

    by_timestamp: dict[float, list[GpuSample]] = {}
    by_gpu: dict[int, list[GpuSample]] = {}
    for sample in samples:
        by_timestamp.setdefault(sample.timestamp, []).append(sample)
        by_gpu.setdefault(sample.gpu_index, []).append(sample)

    total_power = [sum(sample.power_w for sample in batch) for batch in by_timestamp.values()]
    total_memory = [sum(sample.memory_used_mib for sample in batch) for batch in by_timestamp.values()]
    all_utils = [sample.utilization_pct for sample in samples]
    all_temps = [sample.temperature_c for sample in samples]

    per_gpu = {}
    for gpu_index, gpu_samples in sorted(by_gpu.items()):
        per_gpu[str(gpu_index)] = {
            "avg_utilization_pct": average(sample.utilization_pct for sample in gpu_samples),
            "max_utilization_pct": max(sample.utilization_pct for sample in gpu_samples),
            "avg_power_w": average(sample.power_w for sample in gpu_samples),
            "max_power_w": max(sample.power_w for sample in gpu_samples),
            "max_memory_used_mib": max(sample.memory_used_mib for sample in gpu_samples),
            "max_temperature_c": max(sample.temperature_c for sample in gpu_samples),
        }

    return {
        "sample_count": len(samples),
        "avg_utilization_pct": average(all_utils),
        "max_utilization_pct": max(all_utils),
        "avg_total_power_w": average(total_power),
        "max_total_power_w": max(total_power),
        "max_total_memory_mib": max(total_memory),
        "max_temperature_c": max(all_temps),
        "per_gpu": per_gpu,
    }


def average(values: Any) -> float:
    """Return a rounded arithmetic mean for a finite iterable."""
    values_list = list(values)
    return round(sum(values_list) / len(values_list), 3)


def post_json(url: str, payload: dict[str, Any], api_key: str, timeout_seconds: float) -> tuple[int, str]:
    """POST JSON to Guardian and return status/body."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return response.status, response.read().decode("utf-8")


def reset_guardian_after_timeout() -> str:
    """Best-effort local reset to prevent orphaned llama-server GPU burn."""
    if shutil.which("sudo") is None:
        return "skipped: sudo not found"

    kill_result = subprocess.run(["sudo", "pkill", "-9", "llama-server"], capture_output=True, text=True)
    restart_result = subprocess.run(
        ["sudo", "systemctl", "restart", "llama-guardian"], capture_output=True, text=True
    )
    return (
        f"pkill_rc={kill_result.returncode}; "
        f"restart_rc={restart_result.returncode}; "
        f"pkill_stderr={kill_result.stderr.strip()[:200]}; "
        f"restart_stderr={restart_result.stderr.strip()[:200]}"
    )


def run_benchmark(
    args: argparse.Namespace,
    target_tokens: int,
    max_output_tokens: int,
    task: str,
    disable_thinking: bool,
) -> dict[str, Any]:
    """Run a single benchmark request."""
    payload = build_payload(
        args.model,
        target_tokens,
        max_output_tokens,
        args.temperature,
        disable_thinking,
        args.run_name,
        task,
    )
    payload_bytes = len(json.dumps(payload).encode("utf-8"))
    endpoint = args.base_url.rstrip("/") + "/chat/completions"
    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    status = "unknown"
    http_status: int | None = None
    response_text = ""
    content_text = ""
    reasoning_text = ""
    finish_reason = ""
    marker_found = False
    usage_prompt_tokens: int | None = None
    usage_completion_tokens: int | None = None
    usage_total_tokens: int | None = None
    estimated_content_tokens: int | None = None
    estimated_reasoning_tokens: int | None = None
    error_text = ""
    reset_result = "not-needed"
    expected_marker = f"KYBERM0NK_CONTEXT_{target_tokens}"

    with GpuSampler(args.gpu_sample_interval) as sampler:
        try:
            http_status, response_body = post_json(endpoint, payload, args.api_key, args.timeout)
            response_json = json.loads(response_body)
            choice = response_json.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = response_json.get("usage", {})
            content_text = message.get("content") or ""
            reasoning_text = message.get("reasoning_content") or message.get("reasoning") or ""
            response_text = content_text or reasoning_text
            finish_reason = choice.get("finish_reason") or ""
            marker_found = expected_marker in response_text
            usage_prompt_tokens = usage.get("prompt_tokens")
            usage_completion_tokens = usage.get("completion_tokens")
            usage_total_tokens = usage.get("total_tokens")
            estimated_content_tokens, estimated_reasoning_tokens = estimate_completion_split(
                len(content_text), len(reasoning_text), usage_completion_tokens
            )
            status = "ok" if http_status == 200 else "http-error"
        except TimeoutError as exc:
            status = "timeout"
            error_text = str(exc)
        except urllib.error.HTTPError as exc:
            status = "http-error"
            http_status = exc.code
            error_text = exc.read().decode("utf-8", errors="replace")[:2000]
            try:
                error_json = json.loads(error_text)
                usage_prompt_tokens = error_json.get("error", {}).get("n_prompt_tokens")
            except json.JSONDecodeError:
                pass
        except urllib.error.URLError as exc:
            status = "url-error"
            error_text = str(exc)
        except Exception as exc:  # noqa: BLE001 - benchmark must record unexpected failures.
            status = "error"
            error_text = repr(exc)

    elapsed_seconds = round(time.perf_counter() - start_time, 3)
    if status in {"timeout", "url-error"} and args.reset_on_timeout:
        reset_result = reset_guardian_after_timeout()

    return {
        "started_at": started_at,
        "model": args.model,
        "target_context_tokens": target_tokens,
        "task": task,
        "thinking_mode": thinking_label(disable_thinking),
        "thinking_enabled": not disable_thinking,
        "max_output_tokens": max_output_tokens,
        "context_limit_tokens": args.context_limit,
        "requested_total_budget_tokens": target_tokens + max_output_tokens + args.overhead_tokens,
        "budget_status": requested_budget_status(
            args.context_limit, target_tokens, max_output_tokens, args.overhead_tokens
        ),
        "payload_bytes": payload_bytes,
        "timeout_seconds": args.timeout,
        "elapsed_seconds": elapsed_seconds,
        "status": status,
        "http_status": http_status,
        "response_preview": response_text[:500],
        "response_chars": len(response_text),
        "content_chars": len(content_text),
        "reasoning_chars": len(reasoning_text),
        "finish_reason": finish_reason,
        "marker_found": marker_found,
        "usage_prompt_tokens": usage_prompt_tokens,
        "usage_completion_tokens": usage_completion_tokens,
        "usage_total_tokens": usage_total_tokens,
        "estimated_content_tokens": estimated_content_tokens,
        "estimated_reasoning_tokens": estimated_reasoning_tokens,
        "remaining_context_after_prompt_tokens": (
            args.context_limit - usage_prompt_tokens
            if args.context_limit is not None and usage_prompt_tokens is not None
            else None
        ),
        "remaining_context_after_completion_tokens": (
            args.context_limit - usage_total_tokens
            if args.context_limit is not None and usage_total_tokens is not None
            else None
        ),
        "error": error_text,
        "reset_result": reset_result,
        "gpu": summarize_gpu(sampler.samples),
    }


def write_outputs(output_dir: Path, run_name: str, results: list[dict[str, Any]]) -> tuple[Path, Path]:
    """Write benchmark results to JSONL and CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{run_name}.jsonl"
    csv_path = output_dir / f"{run_name}.csv"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, sort_keys=True) + "\n")

    fieldnames = [
        "started_at",
        "model",
        "target_context_tokens",
        "task",
        "thinking_mode",
        "thinking_enabled",
        "max_output_tokens",
        "context_limit_tokens",
        "requested_total_budget_tokens",
        "budget_status",
        "payload_bytes",
        "timeout_seconds",
        "elapsed_seconds",
        "status",
        "http_status",
        "response_chars",
        "content_chars",
        "reasoning_chars",
        "finish_reason",
        "marker_found",
        "usage_prompt_tokens",
        "usage_completion_tokens",
        "usage_total_tokens",
        "estimated_content_tokens",
        "estimated_reasoning_tokens",
        "remaining_context_after_prompt_tokens",
        "remaining_context_after_completion_tokens",
        "gpu_sample_count",
        "avg_gpu_utilization_pct",
        "max_gpu_utilization_pct",
        "avg_total_power_w",
        "max_total_power_w",
        "max_total_memory_mib",
        "max_temperature_c",
        "reset_result",
        "error",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            gpu = result["gpu"]
            writer.writerow(
                {
                    "started_at": result["started_at"],
                    "model": result["model"],
                    "target_context_tokens": result["target_context_tokens"],
                    "task": result["task"],
                    "thinking_mode": result["thinking_mode"],
                    "thinking_enabled": result["thinking_enabled"],
                    "max_output_tokens": result["max_output_tokens"],
                    "context_limit_tokens": result["context_limit_tokens"],
                    "requested_total_budget_tokens": result["requested_total_budget_tokens"],
                    "budget_status": result["budget_status"],
                    "payload_bytes": result["payload_bytes"],
                    "timeout_seconds": result["timeout_seconds"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "status": result["status"],
                    "http_status": result["http_status"],
                    "response_chars": result["response_chars"],
                    "content_chars": result["content_chars"],
                    "reasoning_chars": result["reasoning_chars"],
                    "finish_reason": result["finish_reason"],
                    "marker_found": result["marker_found"],
                    "usage_prompt_tokens": result["usage_prompt_tokens"],
                    "usage_completion_tokens": result["usage_completion_tokens"],
                    "usage_total_tokens": result["usage_total_tokens"],
                    "estimated_content_tokens": result["estimated_content_tokens"],
                    "estimated_reasoning_tokens": result["estimated_reasoning_tokens"],
                    "remaining_context_after_prompt_tokens": result["remaining_context_after_prompt_tokens"],
                    "remaining_context_after_completion_tokens": result[
                        "remaining_context_after_completion_tokens"
                    ],
                    "gpu_sample_count": gpu["sample_count"],
                    "avg_gpu_utilization_pct": gpu["avg_utilization_pct"],
                    "max_gpu_utilization_pct": gpu["max_utilization_pct"],
                    "avg_total_power_w": gpu["avg_total_power_w"],
                    "max_total_power_w": gpu["max_total_power_w"],
                    "max_total_memory_mib": gpu["max_total_memory_mib"],
                    "max_temperature_c": gpu["max_temperature_c"],
                    "reset_result": result["reset_result"],
                    "error": result["error"],
                }
            )

    return jsonl_path, csv_path


def load_existing_results(output_dir: Path, run_name: str) -> list[dict[str, Any]]:
    """Load existing JSONL results for a resumable matrix run."""
    jsonl_path = output_dir / f"{run_name}.jsonl"
    if not jsonl_path.exists():
        return []

    results: list[dict[str, Any]] = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            results.append(json.loads(line))
    return results


def result_case_key(result: dict[str, Any]) -> tuple[int, int, str, str]:
    """Return the matrix identity for a persisted result."""
    return (
        int(result["target_context_tokens"]),
        int(result["max_output_tokens"]),
        str(result["task"]),
        str(result["thinking_mode"]),
    )


def plan_case_key(
    target_tokens: int,
    output_tokens: int,
    task: str,
    disable_thinking: bool,
) -> tuple[int, int, str, str]:
    """Return the matrix identity for a planned case."""
    return (target_tokens, output_tokens, task, thinking_label(disable_thinking))


def spread_order(values: list[int]) -> list[int]:
    """Return values in an early-signal order instead of simple ascending order."""
    sorted_values = sorted(dict.fromkeys(values))
    if len(sorted_values) <= 2:
        return sorted_values

    fractions = [0.0, 0.25, 0.5, 0.125, 0.375, 0.75, 0.875, 0.625, 1.0]
    ordered: list[int] = []
    for fraction in fractions:
        index = round((len(sorted_values) - 1) * fraction)
        value = sorted_values[index]
        if value not in ordered:
            ordered.append(value)
    for value in sorted_values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def decision_phase(output_tokens: int, task: str) -> int:
    """Rank matrix cases by how useful they are for a fast settings decision."""
    if task == "marker" and output_tokens == 32:
        return 0
    if task == "long-decode" and output_tokens in {1024, 4096, 8192}:
        return 1
    if task == "reasoning-stress" and output_tokens in {1024, 4096}:
        return 2
    if task == "long-decode" and output_tokens == 16384:
        return 3
    if task == "marker":
        return 4
    if task == "reasoning-stress":
        return 5
    return 6


def order_plan(plan: list[PlanItem], args: argparse.Namespace, sizes: list[int], output_sizes: list[int]) -> list[PlanItem]:
    """Order the benchmark matrix for either reproducibility or early signal."""
    if args.order == "ordered":
        return plan
    if args.order == "shuffle":
        shuffled = list(plan)
        random.Random(args.seed).shuffle(shuffled)
        return shuffled

    input_rank = {value: index for index, value in enumerate(spread_order(sizes))}
    preferred_outputs = [32, 1024, 4096, 8192, 16384, 32768]
    output_order = [value for value in preferred_outputs if value in output_sizes]
    output_order.extend(value for value in sorted(output_sizes) if value not in output_order)
    output_rank = {value: index for index, value in enumerate(output_order)}

    def priority(item: PlanItem) -> tuple[int, int, int, int, int]:
        target_tokens, output_tokens, task, disable_thinking = item
        budget_status = requested_budget_status(args.context_limit, target_tokens, output_tokens, args.overhead_tokens)
        budget_penalty = 1 if budget_status == "over-budget" else 0
        thinking_rank = 0 if not disable_thinking else 1
        return (
            budget_penalty,
            decision_phase(output_tokens, task),
            input_rank[target_tokens],
            output_rank[output_tokens],
            thinking_rank,
        )

    return sorted(plan, key=priority)


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI parser."""
    env = load_dotenv(REPO_ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=env.get("GUARDIAN_HOST_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--model", default=env.get("DEFAULT_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-key", default=env.get("GUARDIAN_API_KEY") or os.environ.get("GUARDIAN_API_KEY"))
    parser.add_argument("--preset", choices=sorted(PRESETS), default="ramp")
    parser.add_argument("--sizes", help="Comma-separated target context sizes, e.g. 1024,2048,4096")
    parser.add_argument("--task", choices=TASKS, default="marker")
    parser.add_argument("--tasks", help="Comma-separated tasks, or 'all'. Overrides --task.")
    parser.add_argument("--output-sizes", help="Comma-separated completion caps, e.g. 32,1024,8192")
    parser.add_argument("--output-preset", choices=sorted(OUTPUT_PRESETS))
    parser.add_argument(
        "--thinking-modes",
        choices=("default", "disabled", "enabled", "both"),
        default="default",
        help="Run with thinking disabled, enabled, both, or the legacy --enable-thinking/default setting.",
    )
    parser.add_argument("--context-limit", type=int, help="Model context window for budget metadata/skips.")
    parser.add_argument(
        "--overhead-tokens",
        type=int,
        default=256,
        help="Approximate chat-template/system overhead used for pre-run context budget checks.",
    )
    parser.add_argument(
        "--skip-over-context",
        action="store_true",
        help="Record and skip combos whose approximate input+output budget exceeds --context-limit.",
    )
    parser.add_argument("--cooldown-seconds", type=float, default=0.0)
    parser.add_argument("--fail-fast", action="store_true", help="Stop after the first non-ok result.")
    parser.add_argument("--plan-only", action="store_true", help="Print the matrix plan without running requests.")
    parser.add_argument("--resume", action="store_true", help="Skip matrix cases already present in the run JSONL file.")
    parser.add_argument(
        "--order",
        choices=("ordered", "decision", "shuffle"),
        default="ordered",
        help="Matrix order: ordered is reproducible, decision gathers early tuning signal first, shuffle spreads bias.",
    )
    parser.add_argument("--seed", type=int, default=1337, help="Seed for --order shuffle.")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--max-output-tokens", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--enable-thinking",
        action="store_false",
        dest="disable_thinking",
        help="Leave model reasoning enabled. Default disables Qwen-style thinking for cleaner latency tests.",
    )
    parser.add_argument("--gpu-sample-interval", type=float, default=1.0)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--run-name", default=datetime.now(timezone.utc).strftime("context_benchmark_%Y%m%dT%H%M%SZ"))
    parser.add_argument(
        "--no-reset-on-timeout",
        action="store_false",
        dest="reset_on_timeout",
        help="Do not restart Guardian/kill llama-server after a timed out request.",
    )
    parser.set_defaults(reset_on_timeout=True)
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_arg_parser()
    args = parser.parse_args()
    if not args.api_key:
        parser.error("GUARDIAN_API_KEY is required in .env or via --api-key")

    try:
        sizes = parse_sizes(args.sizes, args.preset)
        output_sizes = parse_output_sizes(args)
        tasks = parse_tasks(args.tasks, args.task)
    except ValueError as exc:
        parser.error(str(exc))
    thinking_modes = parse_thinking_modes(args)
    plan = order_plan(list(product(sizes, output_sizes, tasks, thinking_modes)), args, sizes, output_sizes)

    print(f"Benchmarking {args.model} via {args.base_url.rstrip('/')}")
    print(f"Inputs: {sizes}")
    print(f"Output caps: {output_sizes}")
    print(f"Tasks: {tasks}")
    print(f"Thinking modes: {[thinking_label(mode) for mode in thinking_modes]}")
    print(f"Order: {args.order}")
    print(f"Matrix cases: {len(plan)}")
    if args.plan_only:
        for target_tokens, output_tokens, task, disable_thinking in plan:
            budget_status = requested_budget_status(
                args.context_limit, target_tokens, output_tokens, args.overhead_tokens
            )
            print(
                "  "
                f"input={target_tokens} output_cap={output_tokens} task={task} "
                f"thinking={thinking_label(disable_thinking)} budget={budget_status}"
            )
        return 0

    results: list[dict[str, Any]] = load_existing_results(args.output_dir, args.run_name) if args.resume else []
    completed_keys = {result_case_key(result) for result in results}
    if args.resume:
        print(f"Resume mode: loaded {len(results)} existing result rows")
    for target_tokens, output_tokens, task, disable_thinking in plan:
        planned_key = plan_case_key(target_tokens, output_tokens, task, disable_thinking)
        if planned_key in completed_keys:
            print(
                "\n↷ "
                f"input={target_tokens} output_cap={output_tokens} task={task} "
                f"thinking={thinking_label(disable_thinking)} already recorded"
            )
            continue

        budget_status = requested_budget_status(args.context_limit, target_tokens, output_tokens, args.overhead_tokens)
        print(
            "\n▶ "
            f"input={target_tokens} output_cap={output_tokens} task={task} "
            f"thinking={thinking_label(disable_thinking)} budget={budget_status}"
        )
        if args.skip_over_context and budget_status == "over-budget":
            result = build_skipped_result(
                args, target_tokens, output_tokens, task, disable_thinking, "skipped approximate context budget"
            )
            results.append(result)
            completed_keys.add(planned_key)
            write_outputs(args.output_dir, args.run_name, results)
            print("  status=skipped reason=approximate context budget")
            continue

        result = run_benchmark(args, target_tokens, output_tokens, task, disable_thinking)
        results.append(result)
        completed_keys.add(planned_key)
        write_outputs(args.output_dir, args.run_name, results)
        gpu = result["gpu"]
        print(
            "  "
            f"status={result['status']} elapsed={result['elapsed_seconds']}s "
            f"prompt={result['usage_prompt_tokens']} completion={result['usage_completion_tokens']} "
            f"max_gpu={gpu['max_utilization_pct']}% max_power={gpu['max_total_power_w']}W "
            f"reset={result['reset_result']}"
        )
        if result["status"] != "ok" and args.fail_fast:
            print(f"  stopping after {result['status']} to avoid stacking broken requests")
            break
        if args.cooldown_seconds > 0:
            time.sleep(args.cooldown_seconds)

    jsonl_path, csv_path = write_outputs(args.output_dir, args.run_name, results)
    print(f"\nWrote JSONL: {jsonl_path}")
    print(f"Wrote CSV:   {csv_path}")
    return 0 if all(result["status"] == "ok" for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
