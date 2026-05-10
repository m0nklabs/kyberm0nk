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
PROJECT_SOURCE="${REPO_ROOT}/configs/crewai/main_quest_project"
PROJECT_TARGET="/tmp/kyber-main-quest-project"

if [[ -f "${CREWAI_STUDIO_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${CREWAI_STUDIO_DIR}/.env"
  set +a
fi

if ! docker inspect "${CREWAI_STUDIO_WEB_CONTAINER}" >/dev/null 2>&1; then
  log "CrewAI-Studio container ${CREWAI_STUDIO_WEB_CONTAINER} is not running. Run scripts/crewai_studio_bootstrap.sh first."
  exit 1
fi

docker exec "${CREWAI_STUDIO_WEB_CONTAINER}" rm -rf "${PROJECT_TARGET}"
docker cp "${PROJECT_SOURCE}" "${CREWAI_STUDIO_WEB_CONTAINER}:${PROJECT_TARGET}"
docker exec "${CREWAI_STUDIO_WEB_CONTAINER}" python "${PROJECT_TARGET}/crew.py" --dry-run
