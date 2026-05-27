#!/usr/bin/env bash
# KyberM0nk: launch Agent Zero web UI from the host-native runtime.
#
# This wires Guardian as Agent Zero's chat & utility model provider,
# starts run_ui.py on 0.0.0.0:50001 from ~/agentzero, and waits for /health.
#
# Web UI: http://127.0.0.1:50001 on the host.
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

foreground_mode=0
if [[ "${1:-}" == "--foreground" ]]; then
    foreground_mode=1
    shift
fi

if [[ "$#" -gt 0 ]]; then
    echo "usage: $0 [--foreground]" >&2
    exit 2
fi

UI_PORT="${AGENT_ZERO_PORT:-50001}"
runtime_token_path="${AGENT_ZERO_RUNTIME_SECRETS}/github_token"
ssh_key_path="${WINDOWS_UNREAL_SSH_KEY_PATH:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
log_dir="${AGENT_ZERO_ROOT}/logs/kyberm0nk"
log_file="${log_dir}/web.log"

ensure_agent_zero_root
ensure_agent_zero_runtime_dirs

if ! "${AGENT_ZERO_PYTHON}" - <<'PY' >/dev/null 2>&1
from pathlib import Path

path = Path('/home/flip/agentzero/plugins/_code_execution/tools/code_execution_tool.py')
text = path.read_text(errors='ignore') if path.exists() else ''
stale = (
    'Blocked a risky Windows SSH command' in text
    or 'Use `windows-unreal-probe` for discovery' in text
    or 'Do not retry raw ssh quote variants' in text
)
raise SystemExit(1 if stale else 0)
PY
then
    echo "[agent-zero] warning: stale code_execution_tool guidance detected in host runtime"
fi

echo "[agent-zero] syncing tracked config into host runtime..."
cp ./configs/agent-zero/model_config.json "${AGENT_ZERO_ROOT}/usr/plugins/_model_config/config.json"
rm -f "${AGENT_ZERO_ROOT}/usr/plugins/_model_config/config.yaml"
if [[ -f ./configs/agent-zero/patches/vision_load.py ]]; then
    cp ./configs/agent-zero/patches/vision_load.py "${AGENT_ZERO_ROOT}/tools/vision_load.py"
fi

if [[ "${foreground_mode}" -ne 1 ]] && curl -sSf -m 2 "http://127.0.0.1:${UI_PORT}/api/health" >/dev/null 2>&1; then
    echo "[agent-zero] already healthy at http://127.0.0.1:${UI_PORT}"
    exit 0
fi

if pgrep -f "${AGENT_ZERO_ROOT}/run_ui.py" >/dev/null 2>&1; then
    echo "[agent-zero] clearing stale run_ui.py process before restart..."
    pkill -f "${AGENT_ZERO_ROOT}/run_ui.py" || true
fi

if command -v fuser >/dev/null 2>&1 && fuser "${UI_PORT}/tcp" >/dev/null 2>&1; then
    echo "[agent-zero] clearing stale listener on port ${UI_PORT}..."
    fuser -k "${UI_PORT}/tcp" >/dev/null 2>&1 || sudo -n fuser -k "${UI_PORT}/tcp" >/dev/null 2>&1 || true
fi

echo "[agent-zero] restoring tracked project templates..."
./scripts/provision_agent_zero_projects.sh

github_token_path="${KYBERM0NK_GITHUB_TOKEN_PATH:-${GITHUB_TOKEN_FILE:-${HOME}/.secrets/kyberm0nk_github_token}}"
if [[ -r "${github_token_path}" ]]; then
    echo "[agent-zero] provisioning GitHub push credentials..."
    ./scripts/provision_agent_zero_github.sh
else
    echo "[agent-zero] GitHub token file not found at ${github_token_path}; skipping push credential provisioning"
fi

if [[ -r "${ssh_key_path}" ]]; then
    echo "[agent-zero] provisioning Windows Unreal SSH access..."
    ./scripts/provision_windows_unreal_ssh.sh
else
    echo "[agent-zero] Windows Unreal SSH key not found at ${ssh_key_path}; skipping SSH provisioning"
fi

if [[ "${foreground_mode}" -eq 1 ]]; then
    echo "[agent-zero] starting run_ui.py in foreground..."
    mkdir -p "${log_dir}"
    cd "${AGENT_ZERO_ROOT}"
    exec env \
        HOME="${AGENT_ZERO_RUNTIME_HOME}" \
        PATH="${AGENT_ZERO_BIN_DIR}:$PATH" \
        PYTHONPATH="${AGENT_ZERO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}" \
        KYBERM0NK_GITHUB_TOKEN_FILE="${runtime_token_path}" \
        "${AGENT_ZERO_PYTHON}" run_ui.py --host 0.0.0.0 --port "${UI_PORT}"
fi

echo "[agent-zero] checking if Agent Zero is already running..."
if pgrep -f "${AGENT_ZERO_ROOT}/run_ui.py" >/dev/null 2>&1; then
    echo "[agent-zero] already running; restart with: $0 stop && $0"
else
    echo "[agent-zero] starting run_ui.py in background (logs: ${log_file})..."
    mkdir -p "${log_dir}"
    (
        cd "${AGENT_ZERO_ROOT}"
        env \
            HOME="${AGENT_ZERO_RUNTIME_HOME}" \
            PATH="${AGENT_ZERO_BIN_DIR}:$PATH" \
            PYTHONPATH="${AGENT_ZERO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}" \
            KYBERM0NK_GITHUB_TOKEN_FILE="${runtime_token_path}" \
            "${AGENT_ZERO_PYTHON}" run_ui.py --host 0.0.0.0 --port "${UI_PORT}" \
            </dev/null >"${log_file}" 2>&1 &
    )
fi

echo "[agent-zero] waiting for http://127.0.0.1:${UI_PORT}/api/health ..."
for i in $(seq 1 60); do
    if curl -sSf -m 2 "http://127.0.0.1:${UI_PORT}/api/health" >/dev/null 2>&1; then
        echo "[agent-zero] ✓ alive at http://127.0.0.1:${UI_PORT}"
        echo "[agent-zero] tail -f ${log_file} to follow startup"
        exit 0
    fi
    sleep 2
done

echo "[agent-zero] ✗ timed out waiting for /health" >&2
echo "Last 60 log lines:" >&2
tail -60 "${log_file}" >&2 || true
exit 1
