#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Missing required command: $1"
    exit 1
  fi
}

resolve_python_bin() {
  local candidate="${CREWAI_PYTHON_BIN:-}"
  if [[ -n "${candidate}" ]]; then
    printf '%s\n' "${candidate}"
    return 0
  fi

  for candidate in python3.13 python3.12 python3.11 python3.10; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  log "No supported Python interpreter found for CrewAI. Expected one of: python3.13, python3.12, python3.11, python3.10."
  exit 1
}

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

require_command git

CREWAI_PYTHON_BIN="$(resolve_python_bin)"
require_command "${CREWAI_PYTHON_BIN}"

CREWAI_VENV_DIR="${CREWAI_VENV_DIR:-${HOME}/crewai}"
CREWAI_REQUIREMENTS="${CREWAI_REQUIREMENTS:-${REPO_ROOT}/configs/crewai/requirements.txt}"

if [[ ! -f "${CREWAI_REQUIREMENTS}" ]]; then
  log "Missing CrewAI requirements file: ${CREWAI_REQUIREMENTS}"
  exit 1
fi

mkdir -p "$(dirname "${CREWAI_VENV_DIR}")"

if [[ ! -x "${CREWAI_VENV_DIR}/bin/python" ]]; then
  log "Creating CrewAI virtual environment at ${CREWAI_VENV_DIR} with ${CREWAI_PYTHON_BIN}."
  "${CREWAI_PYTHON_BIN}" -m venv "${CREWAI_VENV_DIR}"
else
  log "Using existing CrewAI virtual environment at ${CREWAI_VENV_DIR}."
fi

log "Installing/updating direct CrewAI runtime dependencies."
"${CREWAI_VENV_DIR}/bin/python" -m pip install --upgrade pip
"${CREWAI_VENV_DIR}/bin/pip" install -r "${CREWAI_REQUIREMENTS}"

log "Direct CrewAI runtime is ready. Use scripts/crewai_main_quest_dry_run.sh to validate the project wiring."
