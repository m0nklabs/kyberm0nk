# NewNexus Agent Instructions

You are building NewNexus, the user's Unreal Engine game.

Use `/a0/usr/projects/newnexus` as the working directory. It is restored by KyberM0nk as a symlink to the persistent checkout under `/workspace/project/.agent-projects/NewNexus`, so it survives Docker rebuilds.

Edit source files in `/a0/usr/projects/newnexus`. Use the Windows workstation only for build/run/editor validation after syncing through Git.

Commit and push from `/a0/usr/projects/newnexus` inside the sandbox. KyberM0nk provisions a GitHub credential helper for the running sandbox; do not push via the Windows workstation and do not put tokens in Git remotes or command output.

Generate Windows validation commands yourself and run them through `ssh unreal-windows "<command>"`. Use Windows for Git sync of the Windows checkout, UnrealBuildTool, project generation, editor launches, and runtime validation. Do not use Windows SSH as the primary source editor; inspect and edit source files directly in `/a0/usr/projects/newnexus`.

Known Windows Unreal install:

- Engine root: `J:\UNREAL_ENGINE\UE_5.7`
- Preferred UnrealBuildTool: `J:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe`
- Required .NET 8 runtime is installed on Windows; UBT no longer fails on the missing `Microsoft.NETCore.App 8.0.0` runtime.
- If UBT fails with `Expecting to find a type to be declared in a module rules named 'VisualStudioTools'`, treat `VisualStudioTools` as optional IDE integration. The focused fix is to set that plugin entry's `Enabled` field to `false` in `NewNexus.uproject`, preserving the rest of the plugin metadata. Do not remove the whole plugin object unless the operator explicitly approves it.

Responsibilities:

- Write gameplay code and Unreal project files.
- Use and integrate assets from `Content/` and `References/`.
- Compile and test through the Windows workstation via `ssh unreal-windows`.
- Report exact commands, results, changed files, and remaining risks.

Loop recovery rules:

- Keep each plan short: at most three concrete steps before using a tool.
- If a command is missing, deprecated, or fails once, record that fact and choose a different direct command. Do not test the same missing command again.
- If you notice yourself restating the same reason or plan, stop the thought chain and run a small state check such as `pwd`, `git status --short`, or report the exact blocker.
- Do not repeat identical or near-identical thoughts. Convert the observation into one next action or a blocker report.
- Deprecated Kyber helper commands are not tools. If one prints `DEPRECATED` or `not found`, never call it again in this task.

Action effectiveness rules:

- Coherent reasoning is not the same as progress. Every tool action must have an expected observable effect before you run it.
- After every command or file edit, compare the result with the previous state and write down the delta in one sentence: what changed, what did not change, and whether the task is closer to done.
- If an action succeeds but does not move the task closer to done, do not repeat that action. Pick a smaller milestone, change strategy, or report the blocker.
- If two consecutive actions produce the same state, stop the current route. Run one state check (`pwd`, `git status --short`, or the smallest relevant validation command), then choose a different route or report why progress is blocked.
- Do not keep cleaning, probing, rebuilding, or re-reading just because those actions are valid. Use them only when they answer a specific unknown or verify a specific change.
- Before editing, name the exact file and the exact intended behavioral change. After editing, inspect or validate only enough to confirm that change.
- If validation is blocked by Git sync, credentials, Windows quoting, or an external service, report that blocker exactly. Do not compensate by making unrelated source edits.
- Prefer a small useful change that can be validated over a broad plausible plan that cannot be proven.

Hard rules:

- Do not use `teams-host`; use `unreal-windows` only.
- Do not work in `/opt/agent-zero/usr/workdir` for this project.
- Do not edit source files directly through `J:\Unreal Projects\NewNexus`; edit the local project workspace and sync the Windows checkout for builds.
- Do not route GitHub pushes through Windows; push from `/a0/usr/projects/newnexus`, then pull on Windows before build validation.
- Do not rely on Kyber NewNexus Windows helper commands. Generate the direct Windows SSH, PowerShell, Git, and Unreal command for the current task.
- Do not delete Unreal plugin metadata just to disable a plugin. Prefer `"Enabled": false` and preserve fields such as `Name`, `SupportedTargetPlatforms`, and `MarketplaceURL` unless explicitly told otherwise.
- Do not commit generated Unreal folders such as `Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`, `Build/`, or `.vs/`.
- If Windows path quoting fails over SSH, stop and report the exact command/output instead of retrying random quote variants.
