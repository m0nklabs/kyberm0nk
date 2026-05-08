#!/usr/bin/env bash
# KyberM0nk: run a goal through the planner -> executor pipeline.
# Wrapper for `python -m cockpit.pipeline run` inside the sandbox container.
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 [--no-execute] [--model NAME] \"<goal>\"" >&2
    exit 2
fi

cd "$(dirname "$0")/.."
exec docker compose exec -T sandbox bash -lc "cd /workspace/kyberm0nk && python -m cockpit.pipeline run $(printf '%q ' "$@")"
