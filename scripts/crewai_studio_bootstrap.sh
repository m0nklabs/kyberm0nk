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

port_is_busy() {
  local port="$1"
  (echo >"/dev/tcp/127.0.0.1/${port}") >/dev/null 2>&1
}

choose_available_port() {
  local port="$1"
  while port_is_busy "${port}"; do
    port=$((port + 1))
  done
  printf '%s\n' "${port}"
}

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

require_command git
require_command docker

CREWAI_STUDIO_REPO="${CREWAI_STUDIO_REPO:-https://github.com/m0nklabs/CrewAI-Studio.git}"
CREWAI_STUDIO_DIR="${CREWAI_STUDIO_DIR:-${REPO_ROOT}/.agent-projects/CrewAI-Studio}"
CREWAI_STUDIO_COMPOSE_PROJECT_NAME="${CREWAI_STUDIO_COMPOSE_PROJECT_NAME:-crewai-studio-kyber}"
CREWAI_STUDIO_PORT="${CREWAI_STUDIO_PORT:-8505}"
CREWAI_STUDIO_REQUESTED_PORT="${CREWAI_STUDIO_PORT}"
if [[ "${CREWAI_STUDIO_AUTO_PORT:-1}" == "1" ]]; then
  CREWAI_STUDIO_PORT="$(choose_available_port "${CREWAI_STUDIO_PORT}")"
  if [[ "${CREWAI_STUDIO_PORT}" != "${CREWAI_STUDIO_REQUESTED_PORT}" ]]; then
    log "Port ${CREWAI_STUDIO_REQUESTED_PORT} is busy; using ${CREWAI_STUDIO_PORT} instead."
  fi
fi
CREWAI_STUDIO_DB_PORT="${CREWAI_STUDIO_DB_PORT:-55432}"
CREWAI_STUDIO_WEB_CONTAINER="${CREWAI_STUDIO_WEB_CONTAINER:-crewai_studio_kyber}"
CREWAI_STUDIO_DB_CONTAINER="${CREWAI_STUDIO_DB_CONTAINER:-crewai_db_kyber}"
CREWAI_STUDIO_REFRESH_ENV="${CREWAI_STUDIO_REFRESH_ENV:-0}"

OPENROUTER_API_KEY_FILE="${OPENROUTER_API_KEY_FILE:-${HOME}/.secrets/openrouter.key}"
if [[ -z "${OPENROUTER_API_KEY:-}" && "${OPENAI_API_KEY:-}" == sk-or-* ]]; then
  OPENROUTER_API_KEY="${OPENAI_API_KEY}"
fi
if [[ -z "${OPENROUTER_API_KEY:-}" && -f "${OPENROUTER_API_KEY_FILE}" ]]; then
  OPENROUTER_API_KEY="$(tr -d '\r\n' < "${OPENROUTER_API_KEY_FILE}")"
fi

if [[ "${GUARDIAN_API_KEY:-}" == "replace-me" ]]; then
  GUARDIAN_API_KEY="sk-guardian-local"
fi

GUARDIAN_API_KEY="${GUARDIAN_API_KEY:-sk-guardian-local}"
GUARDIAN_API_BASE="${CREWAI_STUDIO_GUARDIAN_API_BASE:-${GUARDIAN_API_BASE:-http://host.docker.internal:11434/v1}}"
OPENROUTER_API_BASE="${OPENROUTER_API_BASE:-https://openrouter.ai/api/v1}"
OPENROUTER_MODELS="${OPENROUTER_MODELS:-deepseek/deepseek-v4-pro,deepseek/deepseek-v4-flash,google/gemini-3.1-pro-preview-customtools,moonshotai/kimi-k2.6,anthropic/claude-opus-4.7}"
GUARDIAN_MODELS="${GUARDIAN_MODELS:-gemma4-26b-agent,qwen3-35b-reasoning-agent,qwen3-35b-uncensored}"

mkdir -p "$(dirname "${CREWAI_STUDIO_DIR}")"
if [[ -d "${CREWAI_STUDIO_DIR}/.git" ]]; then
  if [[ -n "$(git -C "${CREWAI_STUDIO_DIR}" status --short)" ]]; then
    log "Using existing CrewAI-Studio checkout with local changes: ${CREWAI_STUDIO_DIR}"
  else
    log "Updating CrewAI-Studio fork checkout."
    git -C "${CREWAI_STUDIO_DIR}" pull --ff-only
  fi
else
  log "Cloning CrewAI-Studio fork to ${CREWAI_STUDIO_DIR}."
  git clone "${CREWAI_STUDIO_REPO}" "${CREWAI_STUDIO_DIR}"
fi

APP_ENV="${CREWAI_STUDIO_DIR}/.env"
if [[ ! -f "${APP_ENV}" || "${CREWAI_STUDIO_REFRESH_ENV}" == "1" ]]; then
  if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
    log "OPENROUTER_API_KEY is empty. Studio will start, but OpenRouter models will fail until .env is filled."
  fi
  umask 077
  cat > "${APP_ENV}" <<ENV
COMPOSE_PROJECT_NAME=${CREWAI_STUDIO_COMPOSE_PROJECT_NAME}
POSTGRES_USER=crewai_user
POSTGRES_PASSWORD=crewai_secret
POSTGRES_DB=crewai
DB_URL=postgresql://crewai_user:crewai_secret@db:5432/crewai
CREWAI_STUDIO_PORT=${CREWAI_STUDIO_PORT}
CREWAI_STUDIO_DB_PORT=${CREWAI_STUDIO_DB_PORT}
CREWAI_STUDIO_WEB_CONTAINER=${CREWAI_STUDIO_WEB_CONTAINER}
CREWAI_STUDIO_DB_CONTAINER=${CREWAI_STUDIO_DB_CONTAINER}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
OPENROUTER_API_BASE=${OPENROUTER_API_BASE}
OPENROUTER_MODELS=${OPENROUTER_MODELS}
GUARDIAN_API_KEY=${GUARDIAN_API_KEY}
GUARDIAN_API_BASE=${GUARDIAN_API_BASE}
GUARDIAN_MODELS=${GUARDIAN_MODELS}
AGENTOPS_ENABLED=False
DEFAULT_LANGUAGE=en
ENV
  log "Wrote ${APP_ENV} with local runtime settings."
else
  log "Using existing ${APP_ENV}. Set CREWAI_STUDIO_REFRESH_ENV=1 to regenerate it."
fi

if [[ ! -f "${CREWAI_STUDIO_DIR}/docker-compose.yaml" ]]; then
  log "Missing docker-compose.yaml in ${CREWAI_STUDIO_DIR}."
  exit 1
fi

log "Starting CrewAI-Studio on http://127.0.0.1:${CREWAI_STUDIO_PORT}."
cd "${CREWAI_STUDIO_DIR}"
COMPOSE_PROJECT_NAME="${CREWAI_STUDIO_COMPOSE_PROJECT_NAME}" docker compose --env-file .env -f docker-compose.yaml up -d --build
log "CrewAI-Studio should be reachable at http://127.0.0.1:${CREWAI_STUDIO_PORT} and http://192.168.1.35:${CREWAI_STUDIO_PORT}."
