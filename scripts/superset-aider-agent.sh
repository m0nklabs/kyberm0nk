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
    printf 'No prompt supplied to Kyber Aider Superset agent.\n' >&2
    exit 64
fi

workspace_path="${SUPERSET_WORKSPACE_PATH:-$PWD}"
if [[ ! -d "$workspace_path" ]]; then
    printf 'Workspace path does not exist: %s\n' "$workspace_path" >&2
    exit 64
fi

timestamp="$(date +"%Y-%m-%d_%H-%M-%S")"
log_file="$DIR/logs/superset/aider_$timestamp.log"
mkdir -p "$(dirname "$log_file")"

printf '[%s] Kyber Aider Superset agent starting in %s\n' "$(date -Iseconds)" "$workspace_path" | tee -a "$log_file"

(
    export ACTIVE_PROJECT="$workspace_path"
    cd "$DIR"
    "${compose_cmd[@]}" run --rm --no-deps -T sandbox aider \
        --yes-always \
        --no-auto-commits \
        --message "$prompt"
) 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$log_file"
