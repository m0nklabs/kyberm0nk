#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$DIR/.env" ]; then
	export $(grep -v '^#' "$DIR/.env" | xargs)
fi

export AIDER_MODEL="openai/qwen3-35b-uncensored"
export OPENAI_API_BASE="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="${AIDER_GUARDIAN_API_KEY:?AIDER_GUARDIAN_API_KEY must be set in .env}"
/home/flip/kyberm0nk/docker/aider/venv/bin/aider --no-git --yes --message "Add a dummy file with 'Hello World'" dummy.txt || true
