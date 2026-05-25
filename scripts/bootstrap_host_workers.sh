#!/usr/bin/env bash
set -euo pipefail

resolve_python_bin() {
    local candidate=""
    for candidate in python3.11 python3.12 python3; do
        if command -v "${candidate}" >/dev/null 2>&1; then
            printf '%s\n' "$(command -v "${candidate}")"
            return 0
        fi
    done
    return 1
}

python_minor_version() {
    local python_bin="$1"
    "${python_bin}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

PYTHON_BIN="${KYBER_WORKERS_PYTHON:-$(resolve_python_bin)}"
KYBER_WORKERS_VENV_DIR="${KYBER_WORKERS_VENV_DIR:-${HOME}/venvs/kyber-workers}"
KYBER_WORKERS_BIN_DIR="${KYBER_WORKERS_BIN_DIR:-${KYBER_WORKERS_VENV_DIR}/bin}"
AIDER_ROOT="${AIDER_ROOT:-${HOME}/aider}"
KYBER_AIDER_VENV_DIR="${KYBER_AIDER_VENV_DIR:-${AIDER_VENV_DIR:-${AIDER_ROOT}/.venv}}"
KYBER_OPENCODE_VENV_DIR="${KYBER_OPENCODE_VENV_DIR:-${KYBER_WORKERS_VENV_DIR}/opencode}"
TARGET_PYTHON_VERSION="$(python_minor_version "${PYTHON_BIN}")"

ensure_worker_venv() {
    local venv_dir="$1"

    if [[ -x "${venv_dir}/bin/python" ]]; then
        local current_python_version
        current_python_version="$(python_minor_version "${venv_dir}/bin/python")"
        if [[ "${current_python_version}" != "${TARGET_PYTHON_VERSION}" ]]; then
            rm -rf "${venv_dir}"
        fi
    fi

    if [[ ! -x "${venv_dir}/bin/python" ]]; then
        "${PYTHON_BIN}" -m venv "${venv_dir}"
    fi

    "${venv_dir}/bin/pip" install --upgrade pip setuptools wheel
}

mkdir -p "$(dirname "${KYBER_WORKERS_VENV_DIR}")"
mkdir -p "${AIDER_ROOT}"

if [[ -f "${KYBER_WORKERS_VENV_DIR}/pyvenv.cfg" ]]; then
    rm -rf "${KYBER_WORKERS_VENV_DIR}"
fi

mkdir -p "${KYBER_WORKERS_BIN_DIR}"

ensure_worker_venv "${KYBER_AIDER_VENV_DIR}"
"${KYBER_AIDER_VENV_DIR}/bin/pip" install "aider-chat"

ensure_worker_venv "${KYBER_OPENCODE_VENV_DIR}"
"${KYBER_OPENCODE_VENV_DIR}/bin/pip" install "open-interpreter" "httpx>=0.28,<1"
"${KYBER_OPENCODE_VENV_DIR}/bin/pip" install "setuptools<81"

ln -sfn "${KYBER_AIDER_VENV_DIR}/bin/aider" "${KYBER_WORKERS_BIN_DIR}/aider"
ln -sfn "${KYBER_OPENCODE_VENV_DIR}/bin/interpreter" "${KYBER_WORKERS_BIN_DIR}/interpreter"

printf '[host-workers] ready: %s\n' "${KYBER_WORKERS_VENV_DIR}"
printf '[host-workers] aider root: %s\n' "${AIDER_ROOT}"
printf '[host-workers] aider venv: %s\n' "${KYBER_AIDER_VENV_DIR}"
printf '[host-workers] opencode venv: %s\n' "${KYBER_OPENCODE_VENV_DIR}"
printf '[host-workers] aider: %s\n' "${KYBER_WORKERS_BIN_DIR}/aider"
printf '[host-workers] interpreter: %s\n' "${KYBER_WORKERS_BIN_DIR}/interpreter"