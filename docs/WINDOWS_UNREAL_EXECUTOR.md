# Windows Unreal Executor

KyberM0nk can hand Unreal build and runtime work to the Windows workstation over SSH.

## Target

| Field | Value |
|-------|-------|
| Host alias from Linux host | `unreal-windows` |
| Host alias inside sandbox | `unreal-windows` |
| Hostname | `192.168.1.245` |
| SSH user | `ue_agent` |
| Desktop / Epic Launcher user | `onyou` |
| Verified host response | `14700K` |

## Key Handling

The dedicated private key stays on the Linux host at:

```text
/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519
```


The provisioning script copies that single key into the sandbox at:

```text
/run/kyberm0nk/secrets/windows_unreal_ed25519
```

Do not mount the full host SSH directory into the sandbox.

Do not rebuild or recreate the image just to add this key. Provision the current container in place:

```bash
scripts/provision_windows_unreal_ssh.sh
```

That script copies only the sandbox SSH config and the dedicated private key into the existing container. It preserves the Agent Zero runtime directory and workdir.

## Direct Windows Commands

Agent Zero should generate Windows commands directly and run them through the `unreal-windows` SSH alias. Do not route NewNexus validation through Kyber wrapper commands.

Use Windows only for environment discovery, Git sync of the Windows checkout, Unreal project generation, UnrealBuildTool, editor launches, and runtime validation. Source inspection and source edits should happen under `/a0/usr/projects/newnexus`.

When Windows-side work is needed, generate the exact command for the task and run it with `ssh unreal-windows "<command>"`. For Windows-specific logic, generate a PowerShell command explicitly rather than relying on a sandbox wrapper. If quoting fails, report the exact command and output instead of retrying random quote variants.

Do not route GitHub commits or pushes through this Windows executor. Agent Zero should commit and push from `/a0/usr/projects/newnexus` in the sandbox, then use Windows only to pull the pushed revision and run Unreal validation.

Deprecated compatibility stubs may exist at the old command names in the sandbox. They intentionally do not run validation; they print a deprecation message and point the worker back to direct `ssh unreal-windows` commands.

Known NewNexus Unreal paths:

```text
Project: J:\UnrealProjects\NewNexus
Engine root: C:\UNREAL_ENGINE\UE_5.7
UnrealBuildTool: C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe
.NET runtime: Microsoft.NETCore.App 8.0.26 installed in C:\Program Files\dotnet
```

The SSH user and GUI user are not the same. Headless SSH commands run under `ue_agent`, while Epic Launcher and Unreal Editor GUI state live under `onyou`. When fixing project discovery or startup browser settings, patch the `onyou` profile:

```text
C:\Users\onyou\AppData\Local\UnrealEngine\5.7\Saved\Config\WindowsEditor\EditorSettings.ini
C:\Users\onyou\AppData\Local\EpicGamesLauncher\Saved\Config\WindowsEditor\GameUserSettings.ini
```

For NewNexus, `VisualStudioTools` is optional and must stay out of `NewNexus.uproject` unless the matching plugin is installed into the source-built engine. If startup reports missing modules, check `C:\Users\onyou\AppData\Local\UnrealBuildTool\Log.txt` before editing source. A `VisualStudioTools` ModuleRules error means the plugin reference is invalid, not that NewNexus code failed to compile.

UnrealBuildTool requires the .NET 8 runtime family. If Windows only has .NET 9, UBT fails before any Unreal build work starts with a missing `Microsoft.NETCore.App 8.0.0` error.

## Validation

Run:

```bash
scripts/test_windows_unreal_ssh.sh
```

Expected checks:

- Host alias can run `whoami` and `hostname`.
- Sandbox alias can run `whoami` and `hostname` through the mounted key.
- The private key path is readable inside the sandbox but remains outside Git.

## Prompt For Agent Zero

Give Agent Zero explicit Windows executor instructions like this:

```text
Use the Windows Unreal executor over SSH.

Connection:
- Generate direct Windows commands yourself and run them through `ssh unreal-windows "<command>"`.
- Use PowerShell explicitly when Windows path handling or Unreal tooling needs it.
- The target is Windows host 14700K over SSH as user ue_agent.
- Do not use teams-host; use unreal-windows only.

First verify access:
1. Run: ssh unreal-windows "whoami"
2. Run: ssh unreal-windows "hostname"

Then inspect the Unreal environment:
1. Find installed Unreal Engine versions under common locations such as C:\Program Files\Epic Games.
2. Find or create the project directory I give you.
3. Before making changes, report the detected Unreal version, project path, and intended build/run command.

For every implementation task:
- Make code changes in the specified project only.
- Run the relevant Unreal build or editor command after changes.
- Report command output summaries and file paths changed.
- If Windows command quoting fails, stop and report the exact command/output instead of trying random quote variants.
```