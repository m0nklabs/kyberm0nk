#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f "$DIR/.env" ]; then echo "❌ ERROR: .env file missing in $DIR"; exit 1; fi
export $(grep -v "^#" "$DIR/.env" | xargs)

if [ -z "$ACTIVE_PROJECT" ] || [ ! -d "$ACTIVE_PROJECT" ]; then echo "❌ ERROR: ACTIVE_PROJECT is not set or does not exist: $ACTIVE_PROJECT"; exit 1; fi

echo "🚀 Checking Sandbox container..."
cd "$DIR"
if ! docker-compose ps --services --filter "status=running" | grep -q "^sandbox$"; then
    echo "📦 Starting unified KyberM0nk sandbox..."
    docker-compose up -d sandbox
fi

echo "📂 Active project: $ACTIVE_PROJECT"

# Note: Aider requires a TTY and shouldn"t pipe to strict logs usually unless handled
docker-compose exec sandbox aider "$@"
