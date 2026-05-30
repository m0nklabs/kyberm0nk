#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADVISOR_STATE_FILE="${AIDER_ADVISOR_STATE_FILE:-${XDG_STATE_HOME:-${HOME}/.local/state}/kyberm0nk/aider_advisor.json}"

# Source the env file
if [ -f "$DIR/.env" ]; then
    export $(grep -v '^#' "$DIR/.env" | xargs)
else
    echo "⚠️  .env file not found. Have you copied .env.example?"
fi

echo "============================================="
echo "🦍 KyberM0nk Workspace Status"
echo "============================================="
echo "Active Project:      ${ACTIVE_PROJECT:-Not Set}"
if [ ! -d "$ACTIVE_PROJECT" ]; then
    echo "                     ❌ Directory does not exist!"
else
    echo "                     ✅ Directory OK"
fi

echo "Reference Projects:  ${REFERENCE_PROJECTS:-None}"
echo "Guardian Gateway:    ${GUARDIAN_BASE_URL:-Not Set}"
echo "Default Model:       ${DEFAULT_MODEL:-Not Set}"
if [ -f "$ADVISOR_STATE_FILE" ]; then
    advisor_line="$(python3 - "$ADVISOR_STATE_FILE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    payload = json.loads(path.read_text(encoding='utf-8'))
except Exception:
    print('Aider advisor: state unreadable')
    raise SystemExit(0)

last_used_date = payload.get('last_used_date') or 'unknown date'
last_used_at = payload.get('last_used_at') or last_used_date
model = payload.get('model') or 'openrouter/openai/gpt-5.5'
print(f'Aider advisor: used today once already at {last_used_at} ({model})') if last_used_date == __import__('datetime').datetime.now().date().isoformat() else print(f'Aider advisor: available once today (last use {last_used_at}, {model})')
PY
)"
else
    advisor_line="Aider advisor: available once per day (OpenRouter GPT-5.5)"
fi
echo "$advisor_line"
echo "Docker socket:       ${ALLOW_DOCKER_SOCKET:-false}"
echo "============================================="
