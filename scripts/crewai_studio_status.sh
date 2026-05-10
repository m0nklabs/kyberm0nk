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
CREWAI_STUDIO_PORT="${CREWAI_STUDIO_PORT:-8505}"

if [[ ! -d "${CREWAI_STUDIO_DIR}" ]]; then
  log "CrewAI-Studio checkout not found. Run scripts/crewai_studio_bootstrap.sh first."
  exit 1
fi

if [[ -f "${CREWAI_STUDIO_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${CREWAI_STUDIO_DIR}/.env"
  set +a
fi

cd "${CREWAI_STUDIO_DIR}"
docker compose --env-file .env -f docker-compose.yaml ps

if command -v curl >/dev/null 2>&1; then
  if curl -fsS -m 5 "http://127.0.0.1:${CREWAI_STUDIO_PORT}/_stcore/health" >/dev/null; then
    log "Streamlit health endpoint is reachable on port ${CREWAI_STUDIO_PORT}."
  else
    log "Streamlit health endpoint is not reachable yet on port ${CREWAI_STUDIO_PORT}."
  fi
fi
