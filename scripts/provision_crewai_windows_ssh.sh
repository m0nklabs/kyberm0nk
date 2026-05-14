#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

key_path="${WINDOWS_UNREAL_SSH_KEY_PATH:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
config_path="configs/ssh/windows-unreal.config"

if [[ ! -r "${key_path}" ]]; then
  echo "[windows-unreal-crewai] missing readable key: ${key_path}" >&2
  exit 1
fi

if [[ ! -r "${config_path}" ]]; then
  echo "[windows-unreal-crewai] missing ssh config: ${config_path}" >&2
  exit 1
fi

container_id="$(docker ps -q -f name=crewai_studio_kyber)"

if [[ -z "${container_id}" ]]; then
  echo "[windows-unreal-crewai] container not found" >&2
  exit 1
fi

if [[ "$(docker inspect --format '{{.State.Running}}' "${container_id}")" != "true" ]]; then
  echo "[windows-unreal-crewai] starting existing container..."
  docker start "${container_id}" >/dev/null
fi

echo "[windows-unreal-crewai] provisioning SSH config/key into ${container_id:0:12}..."
docker exec -u root "${container_id}" sh -lc 'mkdir -p /root/.ssh /run/kyberm0nk/secrets && chmod 700 /root/.ssh'
docker cp "${config_path}" "${container_id}:/root/.ssh/config"
docker cp "${key_path}" "${container_id}:/run/kyberm0nk/secrets/windows_unreal_ed25519"
docker exec -u root "${container_id}" sh -lc 'chown root:root /root/.ssh/config /run/kyberm0nk/secrets/windows_unreal_ed25519 && chmod 600 /root/.ssh/config /run/kyberm0nk/secrets/windows_unreal_ed25519 && ssh -V >/dev/null'

echo "[windows-unreal-crewai] SSH material is ready"
