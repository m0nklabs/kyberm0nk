#!/usr/bin/env bash
set -euo pipefail

alias_name="${WINDOWS_UNREAL_SSH_ALIAS:-unreal-windows}"

usage() {
  printf 'Usage: %s <powershell-command>\n' "$(basename "$0")"
  printf '\nRuns a PowerShell command on the Windows Unreal executor via SSH using -EncodedCommand.\n'
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 64
fi

if ! command -v iconv >/dev/null 2>&1; then
  printf '[windows-pwsh] iconv is required for UTF-16LE encoding\n' >&2
  exit 69
fi

if ! command -v base64 >/dev/null 2>&1; then
  printf '[windows-pwsh] base64 is required for PowerShell encoding\n' >&2
  exit 69
fi

command_text="$*"
encoded_command="$(printf '%s' "${command_text}" | iconv -f UTF-8 -t UTF-16LE | base64 | tr -d '\n')"

if [[ ${#encoded_command} -le 7000 ]]; then
  ssh "${alias_name}" "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand ${encoded_command}"
else
  printf '%s' "${command_text}" | ssh "${alias_name}" "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command -"
fi
