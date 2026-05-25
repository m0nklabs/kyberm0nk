#!/usr/bin/env bash

AGENT_ZERO_ROOT="${AGENT_ZERO_ROOT:-${HOME}/agentzero}"
AGENT_ZERO_VENV_DIR="${AGENT_ZERO_VENV_DIR:-${AGENT_ZERO_ROOT}/.venv}"
AGENT_ZERO_PYTHON="${AGENT_ZERO_PYTHON:-${AGENT_ZERO_VENV_DIR}/bin/python}"
AGENT_ZERO_RUNTIME_HOME="${AGENT_ZERO_RUNTIME_HOME:-${AGENT_ZERO_ROOT}/runtime/home}"
AGENT_ZERO_RUNTIME_SECRETS="${AGENT_ZERO_RUNTIME_SECRETS:-${AGENT_ZERO_ROOT}/runtime/secrets}"
AGENT_ZERO_RUNTIME_SSH_DIR="${AGENT_ZERO_RUNTIME_SSH_DIR:-${AGENT_ZERO_RUNTIME_HOME}/.ssh}"
AGENT_ZERO_BIN_DIR="${AGENT_ZERO_BIN_DIR:-${AGENT_ZERO_ROOT}/bin}"
AGENT_ZERO_COMPAT_ROOT="${AGENT_ZERO_COMPAT_ROOT:-/a0/usr}"

ensure_agent_zero_root() {
    if [[ ! -d "${AGENT_ZERO_ROOT}" ]]; then
        printf '[agent-zero] missing host runtime at %s\n' "${AGENT_ZERO_ROOT}" >&2
        printf '[agent-zero] run scripts/agent_zero_bootstrap.sh first\n' >&2
        exit 1
    fi

    if [[ ! -x "${AGENT_ZERO_PYTHON}" ]]; then
        printf '[agent-zero] missing Python runtime at %s\n' "${AGENT_ZERO_PYTHON}" >&2
        printf '[agent-zero] run scripts/agent_zero_bootstrap.sh first\n' >&2
        exit 1
    fi

    if [[ ! -f "${AGENT_ZERO_ROOT}/run_ui.py" || ! -f "${AGENT_ZERO_ROOT}/agent.py" ]]; then
        printf '[agent-zero] host runtime is incomplete under %s\n' "${AGENT_ZERO_ROOT}" >&2
        exit 1
    fi
}

ensure_agent_zero_runtime_dirs() {
    mkdir -p \
        "${AGENT_ZERO_ROOT}/usr/plugins/_model_config" \
        "${AGENT_ZERO_ROOT}/usr/projects" \
        "${AGENT_ZERO_ROOT}/usr/uploads" \
        "${AGENT_ZERO_RUNTIME_HOME}" \
        "${AGENT_ZERO_RUNTIME_SECRETS}" \
        "${AGENT_ZERO_RUNTIME_SSH_DIR}" \
        "${AGENT_ZERO_BIN_DIR}"
}

normalize_guardian_api_base() {
    printf '%s\n' "${1//host.docker.internal/127.0.0.1}"
}