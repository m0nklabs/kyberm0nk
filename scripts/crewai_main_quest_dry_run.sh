#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

CREWAI_VENV_DIR="${CREWAI_VENV_DIR:-${HOME}/crewai}"
CREWAI_PYTHON="${CREWAI_VENV_DIR}/bin/python"
PROJECT_SOURCE="${REPO_ROOT}/configs/crewai/main_quest_project"
OPENROUTER_API_KEY_FILE="${OPENROUTER_API_KEY_FILE:-${HOME}/.secrets/openrouter.key}"
GITHUB_TOKEN_FILE="${GITHUB_TOKEN_FILE:-${HOME}/.secrets/kyberm0nk_github_token}"
OPENROUTER_API_KEY_FALLBACK_FILE="${HOME}/.secrets/keys/openrouter.key"

normalize_api_base() {
  printf '%s\n' "$1" | sed 's#host\.docker\.internal#127.0.0.1#g'
}

if [[ -z "${OPENROUTER_API_KEY:-}" && -f "${OPENROUTER_API_KEY_FILE}" ]]; then
  OPENROUTER_API_KEY="$(tr -d '\r\n' < "${OPENROUTER_API_KEY_FILE}")"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -f "${OPENROUTER_API_KEY_FALLBACK_FILE}" ]]; then
  OPENROUTER_API_KEY="$(tr -d '\r\n' < "${OPENROUTER_API_KEY_FALLBACK_FILE}")"
fi

if [[ -z "${GITHUB_TOKEN:-}" && -n "${GH_TOKEN:-}" ]]; then
  GITHUB_TOKEN="${GH_TOKEN}"
fi
if [[ -z "${GITHUB_TOKEN:-}" && -f "${GITHUB_TOKEN_FILE}" ]]; then
  GITHUB_TOKEN="$(tr -d '\r\n' < "${GITHUB_TOKEN_FILE}")"
fi

GUARDIAN_API_BASE="$(normalize_api_base "${CREWAI_GUARDIAN_API_BASE:-${CREWAI_STUDIO_GUARDIAN_API_BASE:-${GUARDIAN_API_BASE:-http://127.0.0.1:11434/v1}}}")"

if [[ ! -x "${CREWAI_PYTHON}" ]]; then
  log "CrewAI runtime is missing at ${CREWAI_PYTHON}. Run scripts/crewai_bootstrap.sh first."
  exit 1
fi

export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
export GITHUB_TOKEN="${GITHUB_TOKEN:-}"
export GH_TOKEN="${GITHUB_TOKEN:-}"
export GUARDIAN_API_BASE

"${CREWAI_PYTHON}" "${PROJECT_SOURCE}/crew.py" --dry-run
