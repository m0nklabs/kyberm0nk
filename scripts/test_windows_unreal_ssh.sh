#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

alias_name="${WINDOWS_UNREAL_SSH_ALIAS:-unreal-windows}"

echo "[windows-unreal] host SSH alias: ${alias_name}"
ssh "${alias_name}" "whoami"
ssh "${alias_name}" "hostname"
./scripts/windows_pwsh.sh '[System.Environment]::MachineName'

echo "[windows-unreal] ensuring sandbox is running..."
./scripts/provision_windows_unreal_ssh.sh

echo "[windows-unreal] sandbox SSH alias: unreal-windows"
docker compose exec -T sandbox sh -lc '
set -eu
test -r /run/kyberm0nk/secrets/windows_unreal_ed25519
ssh unreal-windows "whoami"
ssh unreal-windows "hostname"
windows-pwsh "[System.Environment]::MachineName"
windows-unreal-probe
'

echo "[windows-unreal] OK"
