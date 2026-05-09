# Windows Unreal Executor

KyberM0nk can hand Unreal build and runtime work to the Windows workstation over SSH.

## Target

| Field | Value |
|-------|-------|
| Host alias from Linux host | `unreal-windows` |
| Host alias inside sandbox | `unreal-windows` |
| Hostname | `192.168.1.245` |
| User | `onyou` |
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

## Agent Zero Helpers

The Agent Zero sandbox also has two small helper commands provisioned by `scripts/provision_agent_zero_projects.sh`:

```bash
windows-pwsh "<PowerShell command>"
windows-unreal-probe
```

Use these helpers for Windows discovery, Unreal builds, editor launches, and validation commands that involve Windows paths. They are intentionally not source-editing tools; Agent Zero should edit NewNexus under `/a0/usr/projects/newnexus` and use Windows only after syncing for build/run validation.

Do not route GitHub commits or pushes through this Windows executor. Agent Zero should commit and push from `/a0/usr/projects/newnexus` in the sandbox, then use Windows only to pull the pushed revision and run Unreal validation.

Known NewNexus Unreal paths:

```text
Project: J:\Unreal Projects\NewNexus
Engine root: J:\UNREAL_ENGINE\UE_5.7
UnrealBuildTool: J:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe
.NET runtime: Microsoft.NETCore.App 8.0.26 installed in C:\Program Files\dotnet
```

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
- Prefer helper commands in the sandbox: windows-pwsh "<PowerShell command>" or windows-unreal-probe
- Use raw ssh unreal-windows "<command>" only for simple commands without nested Windows path quoting
- The target is Windows host 14700K as user onyou.
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
```