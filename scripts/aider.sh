#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Validate environment and mounts
if [ ! -f "$DIR/.env" ]; then
    echo "❌ ERROR: .env file missing in $DIR"
    exit 1
fi
export $(grep -v '^#' "$DIR/.env" | xargs)

if [ -z "$ACTIVE_PROJECT" ] || [ ! -d "$ACTIVE_PROJECT" ]; then
    echo "❌ ERROR: ACTIVE_PROJECT is not set or does not exist: $ACTIVE_PROJECT"
    exit 1
fi

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$DIR/logs/aider/aider_$TIMESTAMP.log"

echo "🚀 Starting Aider via Docker Compose..."
echo "📂 Active project: $ACTIVE_PROJECT"
echo "📝 Logging to: $LOG_FILE"

docker-compose run --rm aider "$@" 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0 }' | tee -a "$LOG_FILE"
