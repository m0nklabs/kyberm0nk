#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUPERSET_ROOT="${SUPERSET_ROOT:-${HOME}/superset}"
LEGACY_SUPERSET_ROOT="${LEGACY_SUPERSET_ROOT:-${DIR}/tmp/framework-evals/superset}"

if [[ -d "${SUPERSET_ROOT}" ]]; then
    printf '[superset-bootstrap] host checkout already present at %s\n' "${SUPERSET_ROOT}"
    exit 0
fi

if [[ -d "${LEGACY_SUPERSET_ROOT}" ]]; then
    mkdir -p "$(dirname "${SUPERSET_ROOT}")"
    mv "${LEGACY_SUPERSET_ROOT}" "${SUPERSET_ROOT}"
    printf '[superset-bootstrap] moved Superset checkout to %s\n' "${SUPERSET_ROOT}"
    exit 0
fi

printf '[superset-bootstrap] no Superset checkout found at %s or %s\n' "${SUPERSET_ROOT}" "${LEGACY_SUPERSET_ROOT}" >&2
printf '[superset-bootstrap] clone/build the host checkout first, then rerun this wrapper.\n' >&2
exit 1