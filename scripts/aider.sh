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

AIDER_ROOT="${AIDER_ROOT:-${HOME}/aider}"
AIDER_VENV_DIR="${AIDER_VENV_DIR:-${KYBER_AIDER_VENV_DIR:-${AIDER_ROOT}/.venv}}"
AIDER_BIN="${AIDER_BIN:-${AIDER_VENV_DIR}/bin/aider}"
if [[ ! -x "${AIDER_BIN}" ]]; then
    echo "❌ ERROR: aider binary missing at ${AIDER_BIN}"; exit 1
fi

export OPENAI_API_BASE="$(normalize_api_base "${GUARDIAN_BASE_URL}")"
export OPENAI_API_KEY="${GUARDIAN_API_KEY}"

AIDER_MODEL="${AIDER_MODEL:-openai/${DEFAULT_MODEL}}"

echo "📂 Active project: $ACTIVE_PROJECT"

cd "$ACTIVE_PROJECT"

# Note: Aider requires a TTY and shouldn"t pipe to strict logs usually unless handled
"${AIDER_BIN}" --model "${AIDER_MODEL}" "$@"
