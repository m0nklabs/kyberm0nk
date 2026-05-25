#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
printf '[%s] %s\n' "$(date -Is)" "CrewAI-Studio is retired for Kyber. Bootstrapping direct CrewAI runtime instead."
exec "${SCRIPT_DIR}/crewai_bootstrap.sh" "$@"
