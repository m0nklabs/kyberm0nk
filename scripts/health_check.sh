#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$DIR/.env" ]; then
    export $(grep -v '^#' "$DIR/.env" | xargs)
fi

GUARDIAN_PORT=${GUARDIAN_PORT:-11434}
# For host check, stick to 127.0.0.1 since host.docker.internal isn't known to host OS by default
GUARDIAN_HOST_URL="http://127.0.0.1:${GUARDIAN_PORT}/v1/models"
# Force internal docker url just for the network test from inside a container
GUARDIAN_DOCKER_URL="http://host.docker.internal:${GUARDIAN_PORT}/v1/models"
AUTH_HEADER="Authorization: Bearer ${KYBERM0NK_GUARDIAN_API_KEY:-local-dev}"

echo "Checking Guardian host connectivity at ${GUARDIAN_HOST_URL}..."
if curl -H "${AUTH_HEADER}" -s -f -o /dev/null "${GUARDIAN_HOST_URL}"; then
    echo "✅ Host connectivity: OK"
else
    echo "❌ Host connectivity: FAILED"
    exit 1
fi

echo "Checking Guardian Docker connectivity at ${GUARDIAN_DOCKER_URL}..."
if docker run --rm --add-host host.docker.internal:host-gateway curlimages/curl -H "${AUTH_HEADER}" -s -f -m 5 -o /dev/null "${GUARDIAN_DOCKER_URL}"; then
    echo "✅ Docker connectivity: OK"
else
    echo "❌ Docker connectivity: FAILED"
    exit 1
fi

echo "All checks passed. Guardian is ready to serve the stack."
