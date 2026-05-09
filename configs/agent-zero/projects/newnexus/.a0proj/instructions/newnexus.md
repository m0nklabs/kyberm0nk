# NewNexus Agent Instructions

You are building NewNexus, the user's Unreal Engine game.

Use `/a0/usr/projects/newnexus` as the working directory. It is restored by KyberM0nk as a symlink to the persistent checkout under `/workspace/project/.agent-projects/NewNexus`, so it survives Docker rebuilds.

Edit source files in `/a0/usr/projects/newnexus`. Use the Windows workstation only for build/run/editor validation after syncing through Git.

The sandbox provides `windows-pwsh '<PowerShell command>'` and `windows-unreal-probe` helper commands to avoid Windows SSH quote loops. Use them only for Windows discovery, compile, run, and editor validation. Do not use them to edit source files on the Windows checkout.

Known Windows Unreal install:

- Engine root: `J:\UNREAL_ENGINE\UE_5.7`
- Preferred UnrealBuildTool: `J:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe`

Responsibilities:

- Write gameplay code and Unreal project files.
- Use and integrate assets from `Content/` and `References/`.
- Compile and test through the Windows workstation via `ssh unreal-windows`.
- Report exact commands, results, changed files, and remaining risks.

Hard rules:

- Do not use `teams-host`; use `unreal-windows` only.
- Do not work in `/opt/agent-zero/usr/workdir` for this project.
- Do not edit source files directly through `J:\Unreal Projects\NewNexus`; edit the local project workspace and sync the Windows checkout for builds.
- Do not treat `windows-pwsh` as a source editing tool; it is only a Windows build/probe helper.
- Do not commit generated Unreal folders such as `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `Build/`, or `.vs/`.
- If Windows path quoting fails over SSH, stop and report the exact command/output instead of retrying random quote variants.
