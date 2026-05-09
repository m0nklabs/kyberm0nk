# NewNexus Agent Instructions

You are building NewNexus, the user's Unreal Engine game.

Use `/a0/usr/projects/newnexus` as the working directory. It is restored by KyberM0nk as a symlink to the persistent checkout under `/workspace/project/.agent-projects/NewNexus`, so it survives Docker rebuilds.

Responsibilities:

- Write gameplay code and Unreal project files.
- Use and integrate assets from `Content/` and `References/`.
- Compile and test through the Windows workstation via `ssh unreal-windows`.
- Report exact commands, results, changed files, and remaining risks.

Hard rules:

- Do not use `teams-host`; use `unreal-windows` only.
- Do not work in `/opt/agent-zero/usr/workdir` for this project.
- Do not commit generated Unreal folders such as `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `Build/`, or `.vs/`.
- If Windows path quoting fails over SSH, stop and report the exact command/output instead of retrying random quote variants.
