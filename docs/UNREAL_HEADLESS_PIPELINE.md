# Unreal Engine 5: Headless Generation & HISM

## NewNexus UE 5.7 Startup and Visual Studio Recovery (May 13, 2026)

This section documents the recovery path for the NewNexus project on the Windows Unreal host after repeated failed attempts by local agents. Keep this as the canonical checklist before changing project plugins, Visual Studio settings, or Unreal build cache again.

### Environment

| Field | Value |
|-------|-------|
| Windows host | `192.168.1.245` |
| SSH user | `ue_agent` |
| Desktop / Epic Launcher user | `onyou` |
| Engine root | `C:\UNREAL_ENGINE\UE_5.7` |
| Project root | `J:\UnrealProjects\NewNexus` |
| Project file | `J:\UnrealProjects\NewNexus\NewNexus.uproject` |
| UnrealBuildTool | `C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe` |

Headless SSH and CI/CD commands for this workstation run under `ue_agent`. Keep GUI-facing launcher/project-browser fixes anchored to `onyou`, but assume remote PowerShell, UnrealBuildTool, and headless editor runs execute as `ue_agent`.

### Symptom: VS2022 reports missing `v143` and `Win64`

Visual Studio showed:

```text
UE5.vcxproj : warning : The build tools for Visual Studio 2022 (v143) cannot be found.
UE5.vcxproj : warning : Platform 'Win64' referenced in the project file 'UE5' cannot be found.
```

The compiler was actually installed. The missing piece was Visual Studio's MSBuild platform target alias: Unreal-generated projects use `Win64`, while the installed VS2022 MSBuild platform directory only contained `x64`.

Validated state:

```text
C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207
C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VC\v170\Platforms\x64
```

Fix:

```powershell
$platformRoot = "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Microsoft\VC\v170\Platforms"
New-Item -ItemType Junction -Path "$platformRoot\Win64" -Target "$platformRoot\x64"
```

Validate without opening Visual Studio:

```powershell
$msbuild = "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
& $msbuild "J:\UnrealProjects\NewNexus\Intermediate\ProjectFiles\UE5.vcxproj" /p:Configuration=BuiltWithUnrealBuildTool /p:Platform=Win64 /t:ResolveReferences /nologo /verbosity:minimal
& $msbuild "J:\UnrealProjects\NewNexus\NewNexus.sln" /t:ValidateSolutionConfiguration /p:Configuration="Development Editor" /p:Platform=Win64 /nologo /verbosity:minimal
```

Expected result:

```text
VCXPROJ_VALIDATE_EXIT=0
SLN_VALIDATE_EXIT=0
```

### Symptom: Unreal startup says `Missing NewNexus Modules`

The Unreal popup said the `NewNexus` module was missing or built for a different engine version, then failed to rebuild. The real UBT log error was:

```text
Expecting to find a type to be declared in a module rules named 'VisualStudioTools'
```

Root cause: `NewNexus.uproject` had `VisualStudioTools` enabled, but the source-built engine at `C:\UNREAL_ENGINE\UE_5.7` does not contain that plugin. It is optional Visual Studio integration, not the C++ compiler and not required for MCPUnreal or NewNexus builds.

Correct fix: remove the `VisualStudioTools` plugin entry from `NewNexus.uproject`. Do not leave it half-enabled.

Then clean the stale build cache and rebuild manually:

```cmd
C:\UNREAL_ENGINE\UE_5.7\Engine\Build\BatchFiles\Build.bat NewNexusEditor Win64 Development -Project="J:\UnrealProjects\NewNexus\NewNexus.uproject" -WaitMutex -NoHotReloadFromIDE
```

Expected result:

```text
Rebuild All: 1 succeeded, 0 failed, 0 skipped
Result: Succeeded
```

After removing the plugin, regenerate project files:

```cmd
C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe -projectfiles -project="J:\UnrealProjects\NewNexus\NewNexus.uproject" -game -rocket -progress -2022
```

### Symptom: Epic Launcher / Unreal Project Browser does not show `J:\UnrealProjects`

There are two separate config paths involved:

1. Epic Games Launcher config.
2. Unreal Engine 5.7 Project Browser config.

The launcher blog fixes only the first one. The UE 5.7 Project Browser logs showed it scans this per-user editor settings file:

```text
C:\Users\onyou\AppData\Local\UnrealEngine\5.7\Saved\Config\WindowsEditor\EditorSettings.ini
```

Required entry:

```ini
[/Script/UnrealEd.EditorSettings]
CreatedProjectPaths=J:/UnrealProjects
```

Epic Launcher config should contain exactly one active entry:

```text
C:\Users\onyou\AppData\Local\EpicGamesLauncher\Saved\Config\WindowsEditor\GameUserSettings.ini
```

```ini
[Launcher]
CreatedProjectPaths=J:\UnrealProjects
```

If projects show duplicated, remove duplicate `CreatedProjectPaths` entries from inactive `Windows` config variants and keep only the active `WindowsEditor` entries above. `RecentlyOpenedProjectFiles` can still make the current project appear as recent in addition to scan results; that is harmless.

### Do Not Do This

- Do not re-enable `VisualStudioTools` unless the matching plugin is installed into `C:\UNREAL_ENGINE\UE_5.7` and UBT can find its `*.Build.cs` module rules.
- Do not treat `VisualStudioTools` as the VS2022 compiler. The required compiler pieces are the VS C++ toolchain, Windows SDK, MSBuild, and UnrealBuildTool.
- Do not rely on `.uprojectdirs` under `C:\UNREAL_ENGINE\UE_5.7` for `J:\UnrealProjects`; UBT ignores external roots there and prints noise.
- Do not accept the Unreal popup rebuild as a reliable diagnostic. Always read `C:\Users\onyou\AppData\Local\UnrealBuildTool\Log.txt` for the real failure.

## Lessons Learned (May 12, 2026)

### 1. Sourcing Assets Headlessly without Quixel UI
When agents are asked to spawn photorealistic assets (like grass) in Unreal Engine headlessly, relying on Quixel Megascans fails because the tool requires manual UI authentication.
**Solution**: Agents should generate CC0 OBJs on the fly (via Python strings) or download raw FBXs, then use `unreal.AssetImportTask` with `unreal.AssetToolsHelpers` to autonomously inject the meshes into the project without blocking on UI popups.

### 2. File Lock 32 (The "Save Map" DXGI Bug)
`UnrealEditor-Cmd.exe` cannot overwrite the `.umap` that it currently holds in memory (Error Code 32). Overwriting the map directly fails silently or crashes.
**Solution**: Spawn the objects into the loaded memory, then use `unreal.EditorAssetLibrary.duplicate_asset` to burn the memory state to a *NEW* `.umap` file (e.g. `Lvl_Grasslands.umap`). 

### 3. Modifying the Build Cook Target
UAT handles `-allmaps` by skipping procedurally generated maps that were never set via the Editor.
**Solution**: Have Python rewrite `Config/DefaultEngine.ini` (`GameDefaultMap` and `EditorStartupMap`) exactly after duplication. UAT will parse the overridden INI directly and package the new headless map automatically. 

### 4. Hierarchical Instanced Static Meshes (HISM)
Spawning 100,000 normal `StaticMeshActor` blades in Python will freeze the commandlet and completely crash the packaged executable due to draw call limits.
**Solution**: Create one Actor, attach an `unreal.HierarchicalInstancedStaticMeshComponent`, and use `add_instances(valid_transforms_list, False)` to draw massive numbers of meshes with near-zero performance cost.

### CrewAI Application
When generating tasks for CrewAI agents that orchestrate Unreal Engine:
* Provide strict pipelines: Do not tell the agent "make grass". Tell the agent "Write a python script that imports an OBJ, applies it to an HISM component, duplicates the loaded map, and rewrites the INI".
* Use explicit urls or embedded OBJ generation to side-step Quixel login requirements during autonomous CI/CD runs. 

### 5. Downloading Free CC0 Assets Headlessly
Instead of fighting Epic Games' Fab / Quixel login flows or writing custom OBJ geometry strings, Python can be used to dynamically fetch CC0 models from public URLs (e.g. raw `.obj` or `.fbx` files on a github repo, AWS S3, or open asset stores like PolyHaven).
**Solution:** Use Python's `urllib.request.urlopen` with a standard `User-Agent` (to prevent bot-blocks) to pull the asset down into an intermediate folder (`TempAssets`), then import it normally via `AssetImportTask` with `options.import_materials = True` enabled. This keeps the entire pipeline fully automated and headless.

### 6. Live Coding Pipe Freezes (Error 0x5 / 0x6)
When running `UnrealEditor-Cmd.exe` via headless SSH or a CI/CD user (`ue_agent`), the engine attempts to initialize the `LiveCodingServer` via Named Pipes. This fails with `Access Denied` (0x5) or `Invalid Handle` (0x6) due to session constraints and will freeze the process indefinitely.
**Solution:** ALWAYS append the `-NoLiveCoding` flag to any `UnrealEditor-Cmd.exe` invocation. Example:
`UnrealEditor-Cmd.exe <Project.uproject> -ExecutePythonScript="script.py" -NoUI -NullRHI -NoLiveCoding`

### 7. Windows Session 0 Constraints (The Webhook Bridge)
When automating over Windows OpenSSH, commands are executed in "Session 0" (a service session with no desktop). Even with `-NoUI` and `-NoLiveCoding`, `UnrealEditor-Cmd.exe` will often hang indefinitely because its internal components wait for IMM contexts or other UI subsystems that don't exist in Session 0.
**Solution:** Create a lightweight Python Webhook (HTTP server) running on the Windows machine inside the active desktop session (Session 1). SSH triggers this Webhook via `curl`, and the Webhook launches Unreal directly in the desktop session.
* **Process Creation**: Use `subprocess.Popen(..., creationflags=subprocess.DETACHED_PROCESS, stdout=log_file, stderr=subprocess.STDOUT)`. Do **not** combine `DETACHED_PROCESS` with `CREATE_NEW_CONSOLE` or Windows will throw `WinError 87: The parameter is incorrect`.
* **Python Runtime**: Use Unreal's bundled python executable to avoid "Python was not found" app execution alias stubs: `C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\ThirdParty\Python3\Win64\python.exe`
