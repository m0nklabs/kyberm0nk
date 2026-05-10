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
CREWAI_STUDIO_WEB_CONTAINER="${CREWAI_STUDIO_WEB_CONTAINER:-crewai_studio_kyber}"
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

if [[ -f "${CREWAI_STUDIO_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${CREWAI_STUDIO_DIR}/.env"
  set +a
fi

if docker inspect "${CREWAI_STUDIO_WEB_CONTAINER}" >/dev/null 2>&1; then
  docker cp "${IMPORT_TARGET}" "${CREWAI_STUDIO_WEB_CONTAINER}:/tmp/main_quest_studio_import.json"
  docker exec "${CREWAI_STUDIO_WEB_CONTAINER}" python /CrewAI-Studio/scripts/import_crew_json.py /tmp/main_quest_studio_import.json
  log "Main quest crew installed directly into CrewAI-Studio database."
else
  log "CrewAI-Studio container is not running. Start it, then rerun this script to install directly into the database."
fi
