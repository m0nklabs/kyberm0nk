#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

token_path="${KYBERM0NK_GITHUB_TOKEN_PATH:-${GITHUB_TOKEN_FILE:-${HOME}/.secrets/kyberm0nk_github_token}}"
helper_path="configs/agent-zero/bin/github-credential-helper"
newnexus_checkout_path="${NEWNEXUS_CHECKOUT_PATH:-${HOME}/NewNexus}"

if [[ ! -r "${token_path}" ]]; then
  echo "[agent-zero-github] missing readable token file: ${token_path}" >&2
  echo "[agent-zero-github] create a fresh GitHub token there, one token on the first line" >&2
  exit 1
fi

if [[ ! -r "${helper_path}" ]]; then
  echo "[agent-zero-github] missing credential helper: ${helper_path}" >&2
  exit 1
fi

ensure_agent_zero_root
ensure_agent_zero_runtime_dirs

echo "[agent-zero-github] provisioning host GitHub credential helper..."
cp "${helper_path}" "${AGENT_ZERO_BIN_DIR}/kyberm0nk-github-credential"
cp "${token_path}" "${AGENT_ZERO_RUNTIME_SECRETS}/github_token"
chmod 755 "${AGENT_ZERO_BIN_DIR}/kyberm0nk-github-credential"
chmod 600 "${AGENT_ZERO_RUNTIME_SECRETS}/github_token"

HOME="${AGENT_ZERO_RUNTIME_HOME}" git config --global credential.https://github.com.helper "${AGENT_ZERO_BIN_DIR}/kyberm0nk-github-credential"
HOME="${AGENT_ZERO_RUNTIME_HOME}" git config --global credential.https://github.com.username x-access-token
HOME="${AGENT_ZERO_RUNTIME_HOME}" git config --global --add safe.directory "${newnexus_checkout_path}" >/dev/null 2>&1 || true

if git -C "${AGENT_ZERO_COMPAT_ROOT}/projects/newnexus" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "${AGENT_ZERO_COMPAT_ROOT}/projects/newnexus" remote set-url origin https://github.com/m0nklabs/NewNexus.git
  git -C "${AGENT_ZERO_COMPAT_ROOT}/projects/newnexus" ls-remote --heads origin main >/dev/null || true
  echo "[agent-zero-github] checking push credentials with git push --dry-run; no refs will be updated"
  HOME="${AGENT_ZERO_RUNTIME_HOME}" KYBERM0NK_GITHUB_TOKEN_FILE="${AGENT_ZERO_RUNTIME_SECRETS}/github_token" \
    git -C "${AGENT_ZERO_COMPAT_ROOT}/projects/newnexus" push --dry-run origin HEAD:main >/dev/null 2>&1 || true
fi

echo "[agent-zero-github] host GitHub push access is ready"