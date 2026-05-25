#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

resolve_python_bin() {
    local candidate=""
    for candidate in python3.12 python3.11 python3; do
        if command -v "${candidate}" >/dev/null 2>&1; then
            printf '%s\n' "$(command -v "${candidate}")"
            return 0
        fi
    done
    return 1
}

python_bin="${AGENT_ZERO_BOOTSTRAP_PYTHON:-$(resolve_python_bin)}"

if [[ ! -d "${AGENT_ZERO_ROOT}" ]]; then
    git clone https://github.com/frdel/agent-zero.git "${AGENT_ZERO_ROOT}"
fi

if [[ ! -x "${AGENT_ZERO_VENV_DIR}/bin/python" ]]; then
    "${python_bin}" -m venv "${AGENT_ZERO_VENV_DIR}"
fi

"${AGENT_ZERO_VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
"${AGENT_ZERO_VENV_DIR}/bin/pip" install -r "${AGENT_ZERO_ROOT}/requirements.txt"
"${AGENT_ZERO_VENV_DIR}/bin/pip" install litellm
if [[ "${AGENT_ZERO_INSTALL_EXTRA_REQUIREMENTS:-false}" == "true" ]] && [[ -f "${AGENT_ZERO_ROOT}/requirements2.txt" ]]; then
    "${AGENT_ZERO_VENV_DIR}/bin/pip" install -r "${AGENT_ZERO_ROOT}/requirements2.txt"
fi
"${AGENT_ZERO_VENV_DIR}/bin/pip" install "numpy" "scikit-learn" "httpx>=0.28,<1"

ensure_agent_zero_runtime_dirs

printf '[agent-zero-bootstrap] ready: %s\n' "${AGENT_ZERO_ROOT}"
printf '[agent-zero-bootstrap] python: %s\n' "${AGENT_ZERO_PYTHON}"