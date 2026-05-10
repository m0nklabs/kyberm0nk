#!/usr/bin/env bash
# Restart Agent Zero UI after a stuck/repetitive run and reload tracked config.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[agent-zero] stopping stuck run_ui.py if present..."
docker compose exec -T sandbox bash -lc 'pkill -f "[r]un_ui.py" || true'

echo "[agent-zero] applying tracked project templates and model config..."
./scripts/provision_agent_zero_projects.sh --force

echo "[agent-zero] starting UI with fresh runtime config..."
./scripts/agent_zero_up.sh