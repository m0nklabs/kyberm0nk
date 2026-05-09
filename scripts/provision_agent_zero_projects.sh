#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

force=false
if [[ "${1:-}" == "--force" ]]; then
  force=true
fi

template_root="configs/agent-zero/projects"

if [[ ! -d "${template_root}" ]]; then
  echo "[agent-zero-projects] no tracked project templates found"
  exit 0
fi

container_id="$(docker compose ps -q sandbox)"
if [[ -z "${container_id}" ]]; then
  echo "[agent-zero-projects] sandbox container not found; creating without rebuild..."
  docker compose up -d --no-build sandbox >/dev/null
  container_id="$(docker compose ps -q sandbox)"
fi

if [[ -z "${container_id}" ]]; then
  echo "[agent-zero-projects] sandbox container is unavailable" >&2
  exit 1
fi

if [[ "$(docker inspect --format '{{.State.Running}}' "${container_id}")" != "true" ]]; then
  echo "[agent-zero-projects] starting existing sandbox container..."
  docker start "${container_id}" >/dev/null
fi

if [[ -d "${template_root}/newnexus" ]]; then
  ./scripts/ensure_newnexus_checkout.sh
fi

docker compose exec -T sandbox sh -lc 'mkdir -p /opt/agent-zero/usr/projects /a0/usr/projects'

for project_dir in "${template_root}"/*; do
  [[ -d "${project_dir}" ]] || continue

  slug="$(basename "${project_dir}")"
  target="/opt/agent-zero/usr/projects/${slug}"

  if docker compose exec -T sandbox sh -lc "test -e '${target}/.a0proj/project.json'" >/dev/null 2>&1 && [[ "${force}" != true ]]; then
    echo "[agent-zero-projects] ${slug}: exists, keeping runtime copy"
  else
    echo "[agent-zero-projects] ${slug}: restoring tracked template"
    docker compose exec -T sandbox sh -lc "mkdir -p '${target}'"
    docker cp "${project_dir}/." "${container_id}:${target}"
  fi

  if [[ "${slug}" == "newnexus" ]]; then
    docker compose exec -T sandbox sh -lc '
set -eu
target="/a0/usr/projects/newnexus"
source="/workspace/project/.agent-projects/NewNexus"
mkdir -p /a0/usr/projects
if [ -L "${target}" ]; then
  ln -sfn "${source}" "${target}"
elif [ -e "${target}" ]; then
  if [ -z "$(find "${target}" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
    rmdir "${target}"
    ln -s "${source}" "${target}"
  else
    backup="${target}.backup.$(date +%Y%m%d%H%M%S)"
    mv "${target}" "${backup}"
    ln -s "${source}" "${target}"
    echo "[agent-zero-projects] moved non-empty ${target} to ${backup}"
  fi
else
  ln -s "${source}" "${target}"
fi
test -d "${source}"
'
  else
    docker compose exec -T sandbox sh -lc "mkdir -p '/a0/usr/projects/${slug}'"
  fi
done

echo "[agent-zero-projects] done"