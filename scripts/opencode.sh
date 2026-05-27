#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

normalize_api_base() {
    printf '%s\n' "${1//host.docker.internal/127.0.0.1}"
}

if [ ! -f "$DIR/.env" ]; then echo "❌ ERROR: .env file missing in $DIR"; exit 1; fi
active_project_override="${ACTIVE_PROJECT:-}"
set -a
source "$DIR/.env"
set +a
if [[ -n "$active_project_override" ]]; then
    ACTIVE_PROJECT="$active_project_override"
fi

if [ -z "$ACTIVE_PROJECT" ] || [ ! -d "$ACTIVE_PROJECT" ]; then echo "❌ ERROR: ACTIVE_PROJECT is not set or does not exist: $ACTIVE_PROJECT"; exit 1; fi

KYBER_WORKERS_VENV_DIR="${KYBER_WORKERS_VENV_DIR:-${HOME}/venvs/kyber-workers}"
INTERPRETER_BIN="${INTERPRETER_BIN:-${KYBER_WORKERS_VENV_DIR}/bin/interpreter}"
if [[ ! -x "${INTERPRETER_BIN}" ]]; then
    echo "❌ ERROR: interpreter binary missing at ${INTERPRETER_BIN}"; exit 1
fi

OPENCODE_CONTEXT_WINDOW="${OPENCODE_CONTEXT_WINDOW:-65536}"
OPENCODE_MAX_TOKENS="${OPENCODE_MAX_TOKENS:-4096}"
OPENCODE_TEMPERATURE="${OPENCODE_TEMPERATURE:-0.2}"
OPENCODE_MAX_OUTPUT_CHARS="${OPENCODE_MAX_OUTPUT_CHARS:-20000}"
SYSTEM_MESSAGE="$(<"$DIR/configs/opencode/system_message.txt")"
GUARDIAN_API_BASE="$(normalize_api_base "${GUARDIAN_BASE_URL}")"

if [[ -z "${OPENCODE_GUARDIAN_API_KEY:-}" ]]; then
    echo "❌ ERROR: OPENCODE_GUARDIAN_API_KEY missing in $DIR/.env"; exit 1
fi

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$DIR/logs/opencode/opencode_$TIMESTAMP.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "📂 Active project: $ACTIVE_PROJECT"
echo "📝 Logging to: $LOG_FILE"
echo "🧠 OpenCode context: ${OPENCODE_CONTEXT_WINDOW}, max tokens: ${OPENCODE_MAX_TOKENS}, temperature: ${OPENCODE_TEMPERATURE}"

cd "$ACTIVE_PROJECT"

"${INTERPRETER_BIN}" \
    --model "openai/${DEFAULT_MODEL}" \
    --api_base "${GUARDIAN_API_BASE}" \
    --api_key "${OPENCODE_GUARDIAN_API_KEY}" \
    --context_window "${OPENCODE_CONTEXT_WINDOW}" \
    --max_tokens "${OPENCODE_MAX_TOKENS}" \
    --temperature "${OPENCODE_TEMPERATURE}" \
    --max_output "${OPENCODE_MAX_OUTPUT_CHARS}" \
    --system_message "${SYSTEM_MESSAGE}" \
    "$@" 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$LOG_FILE"
