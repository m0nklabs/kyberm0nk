#!/usr/bin/env bash
# Stop the host-native Agent Zero web UI.
set -euo pipefail
cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh
pkill -f "${AGENT_ZERO_ROOT}/run_ui.py" || true
echo "[agent-zero] stopped"
