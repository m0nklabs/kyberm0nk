#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source the env file
if [ -f "$DIR/.env" ]; then
    export $(grep -v '^#' "$DIR/.env" | xargs)
else
    echo "⚠️  .env file not found. Have you copied .env.example?"
fi

echo "============================================="
echo "🦍 KyberM0nk Workspace Status"
echo "============================================="
echo "Active Project:      ${ACTIVE_PROJECT:-Not Set}"
if [ ! -d "$ACTIVE_PROJECT" ]; then
    echo "                     ❌ Directory does not exist!"
else
    echo "                     ✅ Directory OK"
fi

echo "Reference Projects:  ${REFERENCE_PROJECTS:-None}"
echo "Guardian Gateway:    ${GUARDIAN_BASE_URL:-Not Set}"
echo "Default Model:       ${DEFAULT_MODEL:-Not Set}"
echo "Docker socket:       ${ALLOW_DOCKER_SOCKET:-false}"
echo "============================================="
