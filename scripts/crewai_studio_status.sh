#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
printf '[%s] %s\n' "$(date -Is)" "CrewAI-Studio is retired for Kyber. Showing direct CrewAI runtime status instead."
exec "${SCRIPT_DIR}/crewai_status.sh" "$@"
