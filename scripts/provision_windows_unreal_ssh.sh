#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

key_path="${WINDOWS_UNREAL_SSH_KEY_PATH:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
config_path="configs/ssh/windows-unreal.config"

if [[ ! -r "${key_path}" ]]; then
  echo "[windows-unreal] missing readable key: ${key_path}" >&2
  exit 1
fi

if [[ ! -r "${config_path}" ]]; then
  echo "[windows-unreal] missing tracked ssh config: ${config_path}" >&2
  exit 1
fi

ensure_agent_zero_root
ensure_agent_zero_runtime_dirs

runtime_key_path="${AGENT_ZERO_RUNTIME_SECRETS}/windows_unreal_ed25519"
runtime_config_path="${AGENT_ZERO_RUNTIME_SSH_DIR}/config"

echo "[windows-unreal] provisioning SSH config/key into host Agent Zero runtime..."
cp "${key_path}" "${runtime_key_path}"
chmod 600 "${runtime_key_path}"
sed "s#/run/kyberm0nk/secrets/windows_unreal_ed25519#${runtime_key_path}#g" "${config_path}" > "${runtime_config_path}"
chmod 600 "${runtime_config_path}"
command -v ssh >/dev/null 2>&1

echo "[windows-unreal] host Agent Zero SSH material is ready"
