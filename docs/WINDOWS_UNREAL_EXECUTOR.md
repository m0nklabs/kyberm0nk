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
- Run commands with: ssh unreal-windows "<command>"
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