#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$DIR/.env" ]]; then
    set -a
    source "$DIR/.env"
    set +a
fi

compose_cmd=(docker compose)
if ! docker compose version >/dev/null 2>&1; then
    compose_cmd=(docker-compose)
fi

read_prompt() {
    if [[ "$#" -gt 0 ]]; then
        printf '%s\n' "$*"
        return 0
    fi

    if [[ -t 0 ]]; then
        return 0
    fi

    local prompt=""
    local line=""
    while IFS= read -r line; do
        prompt+="$line"$'\n'
    done
    printf '%s' "$prompt"
}

prompt="$(read_prompt "$@")"
if [[ -z "${prompt//[[:space:]]/}" ]]; then
    printf 'No prompt supplied to Kyber OpenCode Superset agent.\n' >&2
    exit 64
fi

workspace_path="${SUPERSET_WORKSPACE_PATH:-$PWD}"
if [[ ! -d "$workspace_path" ]]; then
    printf 'Workspace path does not exist: %s\n' "$workspace_path" >&2
    exit 64
fi

OPENCODE_CONTEXT_WINDOW="${OPENCODE_CONTEXT_WINDOW:-65536}"
OPENCODE_MAX_TOKENS="${OPENCODE_MAX_TOKENS:-4096}"
OPENCODE_TEMPERATURE="${OPENCODE_TEMPERATURE:-0.2}"
OPENCODE_MAX_OUTPUT_CHARS="${OPENCODE_MAX_OUTPUT_CHARS:-20000}"
system_message="$(<"$DIR/configs/opencode/system_message.txt")"

timestamp="$(date +"%Y-%m-%d_%H-%M-%S")"
log_file="$DIR/logs/superset/opencode_$timestamp.log"
mkdir -p "$(dirname "$log_file")"

printf '[%s] Kyber OpenCode Superset agent starting in %s\n' "$(date -Iseconds)" "$workspace_path" | tee -a "$log_file"

(
    export ACTIVE_PROJECT="$workspace_path"
    cd "$DIR"
    ./scripts/opencode.sh "$prompt"
) 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$log_file"
