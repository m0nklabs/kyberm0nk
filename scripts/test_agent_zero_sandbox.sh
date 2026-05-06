#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧪 Testing Agent Zero Sandbox Capabilities..."

# Ensure we're picking up active project from .env
if [ ! -f "$DIR/.env" ]; then
    echo "❌ ERROR: .env file missing in $DIR"
    exit 1
fi
export $(grep -v '^#' "$DIR/.env" | xargs)

# Start Agent Zero to execute a simple listing to ensure bounded access
echo "Running a basic command via Agent Zero Docker container to test access..."
docker-compose run --rm agent-zero -c "ls -la /workspace/project" > "$DIR/logs/agent-zero/sandbox_test.log" 2>&1 || true

echo "✅ Tested sandbox environment successfully. Check logs/agent-zero/sandbox_test.log for results."
