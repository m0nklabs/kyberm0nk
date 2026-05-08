#!/usr/bin/env bash
# Stop Agent Zero web UI inside the sandbox container.
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose exec -T sandbox bash -lc 'pkill -f run_ui.py || true ; echo done'
echo "[agent-zero] stopped"
