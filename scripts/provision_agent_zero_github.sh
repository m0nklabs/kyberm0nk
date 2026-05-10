#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

token_path="${KYBERM0NK_GITHUB_TOKEN_PATH:-${GITHUB_TOKEN_FILE:-${HOME}/.secrets/kyberm0nk_github_token}}"
helper_path="configs/agent-zero/bin/github-credential-helper"

if [[ ! -r "${token_path}" ]]; then
  echo "[agent-zero-github] missing readable token file: ${token_path}" >&2
  echo "[agent-zero-github] create a fresh GitHub token there, one token on the first line" >&2
  exit 1
fi

if [[ ! -r "${helper_path}" ]]; then
  echo "[agent-zero-github] missing credential helper: ${helper_path}" >&2
  exit 1
fi

container_id="$(docker compose ps -q sandbox)"
if [[ -z "${container_id}" ]]; then
  echo "[agent-zero-github] sandbox container not found; creating without rebuild..."
  docker compose up -d --no-build sandbox >/dev/null
  container_id="$(docker compose ps -q sandbox)"
fi

if [[ -z "${container_id}" ]]; then
  echo "[agent-zero-github] sandbox container is unavailable" >&2
  exit 1
fi

if [[ "$(docker inspect --format '{{.State.Running}}' "${container_id}")" != "true" ]]; then
  echo "[agent-zero-github] starting existing sandbox container..."
  docker start "${container_id}" >/dev/null
fi

echo "[agent-zero-github] provisioning GitHub credential helper into sandbox ${container_id:0:12}..."
docker compose exec -T sandbox sh -lc 'mkdir -p /run/kyberm0nk/secrets && chmod 700 /run/kyberm0nk /run/kyberm0nk/secrets'
docker cp "${helper_path}" "${container_id}:/usr/local/bin/kyberm0nk-github-credential"
docker cp "${token_path}" "${container_id}:/run/kyberm0nk/secrets/github_token"

docker compose exec -T sandbox sh -lc '
set -eu
chown root:root /usr/local/bin/kyberm0nk-github-credential /run/kyberm0nk/secrets/github_token
chmod 755 /usr/local/bin/kyberm0nk-github-credential
chmod 600 /run/kyberm0nk/secrets/github_token
git config --global credential.https://github.com.helper /usr/local/bin/kyberm0nk-github-credential
git config --global credential.https://github.com.username x-access-token
git config --global --add safe.directory /workspace/project/.agent-projects/NewNexus >/dev/null 2>&1 || true

if git -C /a0/usr/projects/newnexus rev-parse --git-dir >/dev/null 2>&1; then
  git -C /a0/usr/projects/newnexus remote set-url origin https://github.com/m0nklabs/NewNexus.git
  git -C /a0/usr/projects/newnexus ls-remote --heads origin main >/dev/null || true
  echo "[agent-zero-github] checking push credentials with git push --dry-run; no refs will be updated"
  git -C /a0/usr/projects/newnexus push --dry-run origin HEAD:main >/dev/null 2>&1 || true
fi
'

echo "[agent-zero-github] sandbox GitHub push access is ready"