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

CREWAI_STUDIO_DIR="${CREWAI_STUDIO_DIR:-${REPO_ROOT}/.agent-projects/CrewAI-Studio}"
IMPORT_SOURCE="${REPO_ROOT}/configs/crewai/main_quest_studio_import.json"
IMPORT_DIR="${CREWAI_STUDIO_DIR}/kyber-imports"
IMPORT_TARGET="${IMPORT_DIR}/main_quest_studio_import.json"

if [[ ! -d "${CREWAI_STUDIO_DIR}" ]]; then
  log "CrewAI-Studio checkout not found. Run scripts/crewai_studio_bootstrap.sh first."
  exit 1
fi

mkdir -p "${IMPORT_DIR}"
install -m 0644 "${IMPORT_SOURCE}" "${IMPORT_TARGET}"

log "Seed crew JSON copied to ${IMPORT_TARGET}."
log "Open CrewAI-Studio, go to Import/Export, and import that JSON to create the Kyber main quest crew."
