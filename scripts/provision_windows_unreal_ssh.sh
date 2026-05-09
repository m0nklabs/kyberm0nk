#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

key_path="${WINDOWS_UNREAL_SSH_KEY_PATH:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
config_path="configs/ssh/windows-unreal.config"

if [[ ! -r "${key_path}" ]]; then
  echo "[windows-unreal] missing readable key: ${key_path}" >&2
  exit 1
fi

if [[ ! -r "${config_path}" ]]; then
  echo "[windows-unreal] missing sandbox ssh config: ${config_path}" >&2
  exit 1
fi

container_id="$(docker compose ps -q sandbox)"

if [[ -z "${container_id}" ]]; then
  echo "[windows-unreal] sandbox container not found; creating without rebuild..."
  docker compose up -d --no-build sandbox
  container_id="$(docker compose ps -q sandbox)"
fi

if [[ -z "${container_id}" ]]; then
  echo "[windows-unreal] sandbox container is unavailable" >&2
  exit 1
fi

if [[ "$(docker inspect --format '{{.State.Running}}' "${container_id}")" != "true" ]]; then
  echo "[windows-unreal] starting existing sandbox container..."
  docker start "${container_id}" >/dev/null
fi

echo "[windows-unreal] provisioning SSH config/key into sandbox ${container_id:0:12}..."
docker compose exec -T sandbox sh -lc 'mkdir -p /root/.ssh /run/kyberm0nk/secrets && chmod 700 /root/.ssh'
docker cp "${config_path}" "${container_id}:/root/.ssh/config"
docker cp "${key_path}" "${container_id}:/run/kyberm0nk/secrets/windows_unreal_ed25519"
docker compose exec -T sandbox sh -lc 'chown root:root /root/.ssh/config /run/kyberm0nk/secrets/windows_unreal_ed25519 && chmod 600 /root/.ssh/config /run/kyberm0nk/secrets/windows_unreal_ed25519 && ssh -V >/dev/null'

echo "[windows-unreal] sandbox SSH material is ready"
