#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

mkdir -p "${REPO_ROOT}/logs"
LOG_FILE="${REPO_ROOT}/logs/crewai_live.log"

# Magic setting: Log everything sent to stdout and stderr to the logfile AND screen
exec > >(tee -a "${LOG_FILE}") 2>&1

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  source "${REPO_ROOT}/.env"
  set +a
fi

CREWAI_STUDIO_DIR="${CREWAI_STUDIO_DIR:-${REPO_ROOT}/.agent-projects/CrewAI-Studio}"
CREWAI_STUDIO_WEB_CONTAINER="${CREWAI_STUDIO_WEB_CONTAINER:-crewai_studio_kyber}"
PROJECT_SOURCE="${REPO_ROOT}/configs/crewai/main_quest_project"
PROJECT_TARGET="/tmp/kyber-main-quest-project"

if [[ -f "${CREWAI_STUDIO_DIR}/.env" ]]; then
  set -a
  source "${CREWAI_STUDIO_DIR}/.env"
  set +a
fi

if ! docker inspect "${CREWAI_STUDIO_WEB_CONTAINER}" >/dev/null 2>&1; then
  log "CrewAI-Studio container ${CREWAI_STUDIO_WEB_CONTAINER} is not running."
  exit 1
fi

log "Deploying config to container..."
docker exec "${CREWAI_STUDIO_WEB_CONTAINER}" rm -rf "${PROJECT_TARGET}"
docker cp "${PROJECT_SOURCE}" "${CREWAI_STUDIO_WEB_CONTAINER}:${PROJECT_TARGET}"

log "Starting LIVE CrewAI Run for NewNexus Push Test..."
# Note: Removed -it since background execution does not have a TTY
docker exec "${CREWAI_STUDIO_WEB_CONTAINER}" python "${PROJECT_TARGET}/crew.py" \
  --operator-goal "Bouw een super basis game in Unreal Engine waarin een simpel poppetje kan rondlopen in een omgeving. Compileer dit project via SSH op de Windows PC, en gebruik Github (bijv. id. de 'gh' CLI via SSH) om de gecompileerde game als zip in een GitHub Release te zetten." \
  --project-path "m0nklabs/NewNexus" \
  --current-state "Start van de end-to-end test. Je hebt toegang tot GitHub Push EN een newnexus_windows_ssh tool (aliass 'unreal-windows'). Doe het volgende: 1) Push source code naar GitHub. 2) Gebruik de SSH tool om op de Windows PC naar de map 'L:\\UnrealProjects\\NewNexus' te gaan (bijv. via 'cd /d L:\\UnrealProjects\\NewNexus && ...'), daar een 'git pull' uit te voeren, het project voor Windows te compilen met Unreal Engine tools, het te zippen en als een Release aan te maken via GitHub CLI." \
  --operator-chat-guidance "Bouw de structuur, push deze, en automatiseer vervolgens de build op de remote Windows PC via de windows_ssh_command tool. Gebruik geen cloud GitHub Actions. Alle zware executie (builden/zippen/releasen) vindt plaats via over SSH."
