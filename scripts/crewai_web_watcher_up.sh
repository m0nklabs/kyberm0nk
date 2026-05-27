#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/.env"
  set +a
fi

resolve_python_bin() {
  local candidate="${CREWAI_WATCHER_PYTHON:-}"
  if [[ -n "${candidate}" && -x "${candidate}" ]]; then
    printf '%s\n' "${candidate}"
    return 0
  fi

  if [[ -n "${CREWAI_VENV_DIR:-}" && -x "${CREWAI_VENV_DIR}/bin/python" ]]; then
    printf '%s\n' "${CREWAI_VENV_DIR}/bin/python"
    return 0
  fi

  for candidate in \
    "${HOME}/crewai/bin/python" \
    "${REPO_ROOT}/.venv/crewai/bin/python" \
    "$(command -v python3 2>/dev/null || true)"
  do
    if [[ -n "${candidate}" && -x "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  printf '[crewai-watcher] no Python runtime found\n' >&2
  exit 1
}

mkdir -p "${REPO_ROOT}/logs"
cd "${REPO_ROOT}"

WATCHER_PYTHON="$(resolve_python_bin)"
exec "${WATCHER_PYTHON}" "${REPO_ROOT}/scripts/crewai_web_watcher.py"
