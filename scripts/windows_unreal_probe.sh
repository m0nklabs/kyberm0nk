#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s [windows-project-path]\n' "$(basename "$0")"
  printf '\nDiscovers Unreal Engine installs and .uproject candidates on the Windows executor.\n'
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v windows-pwsh >/dev/null 2>&1; then
  pwsh_runner=(windows-pwsh)
elif [[ -x "${script_dir}/windows_pwsh.sh" ]]; then
  pwsh_runner=("${script_dir}/windows_pwsh.sh")
elif [[ -x "${script_dir}/windows-pwsh" ]]; then
  pwsh_runner=("${script_dir}/windows-pwsh")
else
  printf '[windows-unreal-probe] missing windows-pwsh helper\n' >&2
  exit 69
fi

project_path="$*"
project_path_b64="$(printf '%s' "${project_path}" | base64 | tr -d '\n')"

read -r -d '' ps_script <<PS1 || true
\$ProjectPathBytes = '${project_path_b64}'
\$ProjectPath = ''
if (\$ProjectPathBytes) {
    \$ProjectPath = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(\$ProjectPathBytes))
}

\$ErrorActionPreference = 'Continue'

function Test-Directory {
    param([string]\$Path)
    return [bool](Test-Path -LiteralPath \$Path -PathType Container -ErrorAction SilentlyContinue)
}

function Test-File {
    param([string]\$Path)
    return [bool](Test-Path -LiteralPath \$Path -PathType Leaf -ErrorAction SilentlyContinue)
}

function New-PathCheck {
    param([string]\$Path, [string]\$Kind)
    if (Test-Directory \$Path) {
        \$item = Get-Item -LiteralPath \$Path -ErrorAction SilentlyContinue
        return [ordered]@{ kind = \$Kind; path = \$item.FullName; exists = \$true }
    }
    return [ordered]@{ kind = \$Kind; path = \$Path; exists = \$false }
}

function Find-UProjectCandidates {
    param([string]\$Root, [int]\$MaxDepth = 4, [int]\$Limit = 40)

    \$found = @()
    if (-not (Test-Directory \$Root)) {
        return @()
    }

    \$queue = New-Object 'System.Collections.Generic.Queue[object]'
    \$queue.Enqueue([pscustomobject]@{ Path = \$Root; Depth = 0 })

    while (\$queue.Count -gt 0 -and \$found.Count -lt \$Limit) {
        \$entry = \$queue.Dequeue()
        try {
            foreach (\$file in Get-ChildItem -LiteralPath \$entry.Path -File -Filter '*.uproject' -ErrorAction SilentlyContinue) {
                \$found += [ordered]@{
                    name = \$file.Name
                    path = \$file.FullName
                    directory = \$file.DirectoryName
                }
                if (\$found.Count -ge \$Limit) { break }
            }

            if (\$found.Count -ge \$Limit) { break }

            if (\$entry.Depth -lt \$MaxDepth) {
                foreach (\$dir in Get-ChildItem -LiteralPath \$entry.Path -Directory -ErrorAction SilentlyContinue) {
                    if (\$dir.Name -notmatch '^(Binaries|Build|DerivedDataCache|Intermediate|Saved|\.git|node_modules)$') {
                        \$queue.Enqueue([pscustomobject]@{ Path = \$dir.FullName; Depth = (\$entry.Depth + 1) })
                    }
                }
            }
        }
        catch {
        }
    }

    return @(\$found)
}

\$engineRoots = @(
    'C:\Program Files\Epic Games',
    'C:\Program Files (x86)\Epic Games',
    'D:\Epic Games',
    'D:\Program Files\Epic Games'
) | Select-Object -Unique

\$checkedPaths = @()
\$engineInstallations = @()

foreach (\$root in \$engineRoots) {
    \$checkedPaths += New-PathCheck \$root 'engine_root'
    if (-not (Test-Directory \$root)) { continue }

    foreach (\$dir in Get-ChildItem -LiteralPath \$root -Directory -ErrorAction SilentlyContinue) {
        \$buildBat = Join-Path \$dir.FullName 'Engine\Build\BatchFiles\Build.bat'
        \$editorExe = Join-Path \$dir.FullName 'Engine\Binaries\Win64\UnrealEditor.exe'
        \$hasBuildBat = Test-File \$buildBat
        \$hasEditorExe = Test-File \$editorExe

        if (\$dir.Name -like 'UE_*' -or \$hasBuildBat -or \$hasEditorExe) {
            \$engineInstallations += [ordered]@{
                name = \$dir.Name
                version = (\$dir.Name -replace '^UE_', '')
                path = \$dir.FullName
                build_bat = if (\$hasBuildBat) { \$buildBat } else { \$null }
                editor_exe = if (\$hasEditorExe) { \$editorExe } else { \$null }
            }
        }
    }
}

\$projectRoots = @()
if (\$ProjectPath) { \$projectRoots += \$ProjectPath }
if (\$env:USERPROFILE) {
    \$projectRoots += (Join-Path \$env:USERPROFILE 'Documents\Unreal Projects')
    \$projectRoots += (Join-Path \$env:USERPROFILE 'Documents')
    \$projectRoots += (Join-Path \$env:USERPROFILE 'Desktop')
}
\$projectRoots += 'C:\Unreal Projects'
\$projectRoots += 'D:\Unreal Projects'
\$projectRoots = \$projectRoots | Where-Object { \$_ } | Select-Object -Unique

\$projectCandidates = @()
foreach (\$root in \$projectRoots) {
    \$checkedPaths += New-PathCheck \$root 'project_root'
    \$projectCandidates += Find-UProjectCandidates \$root 4 40
}

\$projectPathExists = \$false
if (\$ProjectPath) {
    \$projectPathExists = Test-Directory \$ProjectPath
}

\$result = [ordered]@{
    generated_at = (Get-Date).ToString('s')
    host = \$env:COMPUTERNAME
    user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    cwd = (Get-Location).Path
    requested_project_path = \$ProjectPath
    requested_project_path_exists = \$projectPathExists
    checked_paths = @(\$checkedPaths)
    unreal_engines = @(\$engineInstallations)
    project_candidates = @(\$projectCandidates | Sort-Object path -Unique)
    agent_zero_guidance = @(
        'Use windows-unreal-probe for discovery instead of raw dir commands over ssh.',
        'Use windows-pwsh for custom commands that involve Windows paths or quotes.',
        'After one failed remote directory command, stop and report the exact command/output instead of retrying quote variants.'
    )
}

\$result | ConvertTo-Json -Depth 8
PS1

"${pwsh_runner[@]}" "${ps_script}"
