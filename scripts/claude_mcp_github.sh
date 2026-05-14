#!/usr/bin/env bash
set -euo pipefail

TOKEN_FILE="${GITHUB_TOKEN_FILE:-/home/flip/.secrets/kyberm0nk_github_token}"

if [[ -z "${GITHUB_PERSONAL_ACCESS_TOKEN:-}" ]]; then
    if [[ -r "$TOKEN_FILE" ]]; then
        GITHUB_PERSONAL_ACCESS_TOKEN="$(<"$TOKEN_FILE")"
    else
        GITHUB_PERSONAL_ACCESS_TOKEN="$(gh auth token)"
    fi
fi

export GITHUB_PERSONAL_ACCESS_TOKEN
exec npx -y @modelcontextprotocol/server-github
