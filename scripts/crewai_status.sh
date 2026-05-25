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

if [[ ! -x "${CREWAI_PYTHON}" ]]; then
  log "CrewAI virtual environment is missing at ${CREWAI_VENV_DIR}. Run scripts/crewai_bootstrap.sh first."
  exit 1
fi

log "CrewAI runtime: ${CREWAI_PYTHON}"
"${CREWAI_PYTHON}" - <<'PY'
import importlib.metadata
import json
import sys

payload = {
    "python": sys.executable,
    "crewai_version": importlib.metadata.version("crewai"),
}
print(json.dumps(payload, indent=2))
PY

"${CREWAI_PYTHON}" "${REPO_ROOT}/scripts/crewai_main_quest_control.py" status --output json
