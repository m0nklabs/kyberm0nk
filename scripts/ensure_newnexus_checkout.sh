#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

repo_url="${NEWNEXUS_REPO_URL:-https://github.com/m0nklabs/NewNexus.git}"
checkout_path="${NEWNEXUS_CHECKOUT_PATH:-${HOME}/NewNexus}"

if [[ -d "${checkout_path}/.git" ]]; then
  echo "[newnexus] checkout ready: ${checkout_path}"
  git -C "${checkout_path}" status --short
  exit 0
fi

if [[ -e "${checkout_path}" ]]; then
  echo "[newnexus] ${checkout_path} exists but is not a Git checkout" >&2
  exit 1
fi

mkdir -p "$(dirname "${checkout_path}")"
echo "[newnexus] cloning ${repo_url} -> ${checkout_path}"
git clone "${repo_url}" "${checkout_path}"