#!/usr/bin/env python3
"""Compact OpenRouter preflight for Kyber review lanes.

The script verifies that Kyber can reach OpenRouter and that configured review
models are visible before Hermes spends a full review budget. It does not modify
provider configuration or repository state.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODELS = (
    "deepseek/deepseek-v4-flash",
    "deepseek/deepseek-v4-pro",
)


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file without shell expansion."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def resolve_value(key: str, env_file_values: dict[str, str], default: str = "") -> str:
    """Return the first non-empty value from process env, .env, or default."""
    value = os.environ.get(key)
    if value:
        return value
    value = env_file_values.get(key)
    if value:
        return value
    return default


def resolve_secret(key: str, file_key: str, env_file_values: dict[str, str]) -> str:
    """Resolve a secret from an env var or a secret file path."""
    value = resolve_value(key, env_file_values, "")
    if value:
        return value
    file_path = resolve_value(file_key, env_file_values, "")
    if not file_path:
        return ""
    candidate = Path(file_path).expanduser()
    if not candidate.exists():
        return ""
    return candidate.read_text(encoding="utf-8").strip()


def normalize_model_id(model: str) -> str:
    """Remove Aider's openrouter/ prefix when checking OpenRouter model IDs."""
    return model.removeprefix("openrouter/").strip()


def request_json(
    url: str,
    *,
    api_key: str,
    timeout_seconds: int,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Call OpenRouter and return JSON payload plus selected response headers."""
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "HTTP-Referer": "https://github.com/m0nklabs/kyberm0nk",
        "X-Title": "KyberM0nk OpenRouter preflight",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8", errors="replace")
            header_map = {key.lower(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"OpenRouter HTTP {exc.code} for {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed for {url}: {exc.reason}") from exc

    try:
        payload_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenRouter returned non-JSON response for {url}: {raw[:300]}") from exc
    if not isinstance(payload_data, dict):
        raise RuntimeError(f"OpenRouter returned unexpected JSON for {url}: {type(payload_data).__name__}")
    return payload_data, header_map


def rate_limit_headers(headers: dict[str, str]) -> dict[str, str]:
    """Extract rate-limit-like headers without assuming provider names."""
    return {
        key: value
        for key, value in headers.items()
        if "rate" in key or "limit" in key or key.startswith("x-ratelimit")
    }


def load_models(base_url: str, api_key: str, timeout_seconds: int) -> tuple[set[str], dict[str, str]]:
    """Fetch available OpenRouter model IDs."""
    payload, headers = request_json(
        f"{base_url.rstrip('/')}/models",
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )
    models = payload.get("data", [])
    if not isinstance(models, list):
        raise RuntimeError("OpenRouter /models response missing data list")
    model_ids = {str(model.get("id")) for model in models if isinstance(model, dict) and model.get("id")}
    return model_ids, headers


def run_tiny_completion(base_url: str, api_key: str, model: str, timeout_seconds: int) -> dict[str, str]:
    """Run a tiny optional chat completion to verify auth beyond model listing."""
    payload, headers = request_json(
        f"{base_url.rstrip('/')}/chat/completions",
        api_key=api_key,
        timeout_seconds=timeout_seconds,
        method="POST",
        payload={
            "model": model,
            "messages": [{"role": "user", "content": "Reply with OK."}],
            "max_tokens": 2,
            "temperature": 0,
        },
    )
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("OpenRouter completion response missing choices")
    return rate_limit_headers(headers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="OpenRouter model ID to check. May be repeated. Defaults to Kyber reviewer models.",
    )
    parser.add_argument(
        "--completion-check",
        action="store_true",
        help="Run one tiny max_tokens=2 chat completion against the first requested model.",
    )
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_values = parse_env_file(ENV_FILE)
    base_url = resolve_value("OPENROUTER_API_BASE", env_values, DEFAULT_BASE_URL).rstrip("/")
    api_key = resolve_secret("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_FILE", env_values)
    requested_models = tuple(normalize_model_id(model) for model in (args.models or DEFAULT_MODELS))

    result: dict[str, Any] = {
        "base_url": base_url,
        "models": list(requested_models),
        "auth_present": bool(api_key),
        "completion_check": bool(args.completion_check),
        "ok": False,
    }

    if not api_key:
        result["error"] = "OPENROUTER_API_KEY or OPENROUTER_API_KEY_FILE is missing"
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"FAIL OpenRouter preflight: {result['error']}")
        return 2

    try:
        available_models, headers = load_models(base_url, api_key, args.timeout)
        missing = [model for model in requested_models if model not in available_models]
        result["available_count"] = len(available_models)
        result["missing_models"] = missing
        result["rate_limit_headers"] = rate_limit_headers(headers)
        if missing:
            result["error"] = "requested model(s) missing from /models"
            if args.json:
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                print(f"FAIL OpenRouter preflight: missing models: {', '.join(missing)}")
            return 1

        if args.completion_check:
            result["completion_rate_limit_headers"] = run_tiny_completion(
                base_url,
                api_key,
                requested_models[0],
                args.timeout,
            )

    except Exception as exc:
        result["error"] = str(exc)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"FAIL OpenRouter preflight: {exc}")
        return 1

    result["ok"] = True
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"OK OpenRouter preflight: {len(requested_models)} model(s) available via {base_url}")
        for model in requested_models:
            print(f"  - {model}")
        headers = result.get("rate_limit_headers") or {}
        if headers:
            print("  rate-limit headers:")
            for key, value in sorted(headers.items()):
                print(f"    {key}: {value}")
        elif not args.completion_check:
            print("  rate-limit headers: none returned by /models")
        if args.completion_check:
            print("  tiny completion check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
