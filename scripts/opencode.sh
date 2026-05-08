#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$DIR/.env" ]; then echo "❌ ERROR: .env file missing in $DIR"; exit 1; fi
set -a
source "$DIR/.env"
set +a

if [ -z "$ACTIVE_PROJECT" ] || [ ! -d "$ACTIVE_PROJECT" ]; then echo "❌ ERROR: ACTIVE_PROJECT is not set or does not exist: $ACTIVE_PROJECT"; exit 1; fi

OPENCODE_CONTEXT_WINDOW="${OPENCODE_CONTEXT_WINDOW:-65536}"
OPENCODE_MAX_TOKENS="${OPENCODE_MAX_TOKENS:-4096}"
OPENCODE_TEMPERATURE="${OPENCODE_TEMPERATURE:-0.2}"
OPENCODE_MAX_OUTPUT_CHARS="${OPENCODE_MAX_OUTPUT_CHARS:-20000}"
SYSTEM_MESSAGE="$(<"$DIR/configs/opencode/system_message.txt")"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$DIR/logs/opencode/opencode_$TIMESTAMP.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "🚀 Checking Sandbox container..."
cd "$DIR"
if ! docker-compose ps --services --filter "status=running" | grep -q "^sandbox$"; then
    echo "📦 Starting unified KyberM0nk sandbox..."
    docker-compose up -d sandbox
fi

echo "📂 Active project: $ACTIVE_PROJECT"
echo "📝 Logging to: $LOG_FILE"
echo "🧠 OpenCode context: ${OPENCODE_CONTEXT_WINDOW}, max tokens: ${OPENCODE_MAX_TOKENS}, temperature: ${OPENCODE_TEMPERATURE}"

docker-compose exec -T sandbox interpreter \
    --model "openai/${DEFAULT_MODEL}" \
    --api_base "${GUARDIAN_BASE_URL}" \
    --api_key "${GUARDIAN_API_KEY}" \
    --context_window "${OPENCODE_CONTEXT_WINDOW}" \
    --max_tokens "${OPENCODE_MAX_TOKENS}" \
    --temperature "${OPENCODE_TEMPERATURE}" \
    --max_output "${OPENCODE_MAX_OUTPUT_CHARS}" \
    --system_message "${SYSTEM_MESSAGE}" \
    "$@" 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$LOG_FILE"
