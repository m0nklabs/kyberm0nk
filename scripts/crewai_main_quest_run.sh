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
OPERATOR_GOAL="${CREWAI_OPERATOR_GOAL:-Bouw een super basis game in Unreal Engine waarin een simpel poppetje kan rondlopen in een omgeving. Compileer dit project via SSH op de Windows PC, en gebruik Github (bijv. id. de 'gh' CLI via SSH) om de gecompileerde game als zip in een GitHub Release te zetten.}"
PROJECT_PATH="${CREWAI_PROJECT_PATH:-m0nklabs/NewNexus}"
CURRENT_STATE="${CREWAI_CURRENT_STATE:-Start van de end-to-end test. Je hebt toegang tot GitHub Push EN een newnexus_windows_ssh tool (aliass 'unreal-windows'). Doe het volgende: 1) Push source code naar GitHub. 2) Gebruik de SSH tool om op de Windows PC naar de map 'L:\\UnrealProjects\\NewNexus' te gaan (bijv. via 'cd /d L:\\UnrealProjects\\NewNexus && ...'), daar een 'git pull' uit te voeren, het project voor Windows te compilen met Unreal Engine tools, het te zippen en als een Release aan te maken via GitHub CLI.}"
OPERATOR_CHAT_GUIDANCE="${CREWAI_OPERATOR_CHAT_GUIDANCE:-Bouw de structuur, push deze, en automatiseer vervolgens de build op de remote Windows PC via de windows_ssh_command tool. Gebruik geen cloud GitHub Actions. Alle zware executie (builden/zippen/releasen) vindt plaats via over SSH.}"

if [[ -f "${CREWAI_STUDIO_DIR}/.env" ]]; then
  set -a
  source "${CREWAI_STUDIO_DIR}/.env"
  set +a
fi

log "Starting CrewAI run via control script..."
python3 "${REPO_ROOT}/scripts/crewai_main_quest_control.py" run \
  --project-id main_quest_project \
  --project-path "${PROJECT_PATH}" \
  --operator-goal "${OPERATOR_GOAL}" \
  --current-state "${CURRENT_STATE}" \
  --operator-chat-guidance "${OPERATOR_CHAT_GUIDANCE}"
