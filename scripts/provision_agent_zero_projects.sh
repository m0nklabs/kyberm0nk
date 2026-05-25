#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source ./scripts/agent_zero_env.sh

force=false
if [[ "${1:-}" == "--force" ]]; then
  force=true
fi

template_root="configs/agent-zero/projects"

if [[ ! -d "${template_root}" ]]; then
  echo "[agent-zero-projects] no tracked project templates found"
  exit 0
fi

newnexus_checkout_path="${NEWNEXUS_CHECKOUT_PATH:-${HOME}/NewNexus}"

ensure_agent_zero_root
ensure_agent_zero_runtime_dirs

if [[ -d "${template_root}/newnexus" ]]; then
  ./scripts/ensure_newnexus_checkout.sh
fi

mkdir -p "${AGENT_ZERO_ROOT}/usr/projects"

if sudo -n true >/dev/null 2>&1; then
  sudo -n mkdir -p "${AGENT_ZERO_COMPAT_ROOT}/projects"
else
  echo "[agent-zero-projects] sudo -n is required to maintain ${AGENT_ZERO_COMPAT_ROOT}" >&2
  exit 1
fi

for deprecated_command in windows-pwsh windows-unreal-probe newnexus-windows-build; do
  cp "configs/agent-zero/bin/${deprecated_command}" "${AGENT_ZERO_BIN_DIR}/${deprecated_command}"
done
chmod 755 "${AGENT_ZERO_BIN_DIR}/windows-pwsh" "${AGENT_ZERO_BIN_DIR}/windows-unreal-probe" "${AGENT_ZERO_BIN_DIR}/newnexus-windows-build"

for project_dir in "${template_root}"/*; do
  [[ -d "${project_dir}" ]] || continue

  slug="$(basename "${project_dir}")"
  target="${AGENT_ZERO_ROOT}/usr/projects/${slug}"

  if [[ -e "${target}/.a0proj/project.json" ]] && [[ "${force}" != true ]]; then
    echo "[agent-zero-projects] ${slug}: exists, keeping runtime copy"
  else
    echo "[agent-zero-projects] ${slug}: restoring tracked template"
    rm -rf "${target}"
    mkdir -p "${target}"
    cp -a "${project_dir}/." "${target}"
  fi

  if [[ "${slug}" == "newnexus" ]]; then
    source_path="${newnexus_checkout_path}"
    compat_target="${AGENT_ZERO_COMPAT_ROOT}/projects/newnexus"
    test -d "${source_path}"
    if [[ -L "${compat_target}" ]]; then
      sudo -n rm -f "${compat_target}"
    fi
    sudo -n ln -sfn "${AGENT_ZERO_ROOT}/usr/uploads" "${AGENT_ZERO_COMPAT_ROOT}/uploads"
    HOME="${AGENT_ZERO_RUNTIME_HOME}" git config --global --add safe.directory "${source_path}" >/dev/null 2>&1 || true
  else
    sudo -n mkdir -p "${AGENT_ZERO_COMPAT_ROOT}/projects/${slug}"
  fi
done

echo "[agent-zero-projects] done"