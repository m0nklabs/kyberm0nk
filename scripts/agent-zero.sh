#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$DIR/scripts/agent_zero_env.sh"

if [ ! -f "$DIR/.env" ]; then echo "❌ ERROR: .env file missing in $DIR"; exit 1; fi
active_project_override="${ACTIVE_PROJECT:-}"
set -a
source "$DIR/.env"
set +a
if [[ -n "$active_project_override" ]]; then
    ACTIVE_PROJECT="$active_project_override"
fi

if [ -z "$ACTIVE_PROJECT" ] || [ ! -d "$ACTIVE_PROJECT" ]; then echo "❌ ERROR: ACTIVE_PROJECT is not set or does not exist: $ACTIVE_PROJECT"; exit 1; fi

ensure_agent_zero_root
ensure_agent_zero_runtime_dirs

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$DIR/logs/agent-zero/agent-zero_$TIMESTAMP.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "📂 Active project: $ACTIVE_PROJECT"
echo "📝 Logging to: $LOG_FILE"

cd "$ACTIVE_PROJECT"

env \
    HOME="${AGENT_ZERO_RUNTIME_HOME}" \
    PATH="${AGENT_ZERO_BIN_DIR}:$PATH" \
    PYTHONPATH="${AGENT_ZERO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}" \
    KYBERM0NK_GITHUB_TOKEN_FILE="${AGENT_ZERO_RUNTIME_SECRETS}/github_token" \
    "${AGENT_ZERO_PYTHON}" "${AGENT_ZERO_ROOT}/run_ui.py" "$@" 2>&1 | tee -a "$LOG_FILE"
