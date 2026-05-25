#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

alias_name="${WINDOWS_UNREAL_SSH_ALIAS:-unreal-windows}"

echo "[windows-unreal] host SSH alias: ${alias_name}"
ssh "${alias_name}" "whoami"
ssh "${alias_name}" "hostname"

echo "[windows-unreal] provisioning Agent Zero runtime SSH..."
./scripts/provision_windows_unreal_ssh.sh

echo "[windows-unreal] Agent Zero runtime SSH alias: ${alias_name}"
HOME="${AGENT_ZERO_RUNTIME_HOME}" ssh -F "${AGENT_ZERO_RUNTIME_SSH_DIR}/config" "${alias_name}" "whoami"
HOME="${AGENT_ZERO_RUNTIME_HOME}" ssh -F "${AGENT_ZERO_RUNTIME_SSH_DIR}/config" "${alias_name}" "hostname"

echo "[windows-unreal] OK"
