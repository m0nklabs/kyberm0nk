# Security Model

KyberM0nk is allowed to automate code work, but it should start conservative.

## Trust Boundaries

### Trusted

- The operator-controlled host.
- Guardian proxy on port `11434`.
- The selected active project when mounted read-write.

### Untrusted or Restricted

- Reference repositories: read-only.
- Tool containers: no broad host access by default.
- Docker socket: disabled by default.
- External model providers: optional fallback only.

## Docker Socket Policy

Do not mount `/var/run/docker.sock` by default.

If a task requires Docker control from inside a container:

1. Document why host Docker access is required.
2. Prefer a narrow wrapper script on the host.
3. Enable only for that task.
4. Disable it afterwards.

## Mount Policy

Active project:

```text
rw
```

Reference projects:

```text
ro
```

Secrets:

```text
never committed
mounted only when required
```

## Guardian Access

Tools should access Guardian through:

```text
http://host.docker.internal:11434/v1
```

Tools must not call:

```text
http://127.0.0.1:11440
```

Port `11440` is the backend managed by Guardian.

## Windows Unreal Executor SSH

Agent Zero may access the Windows Unreal executor through a dedicated SSH key for coding and build automation.

Rules:

- Provision only the dedicated private key into the sandbox, never the full host `~/.ssh` directory.
- Keep the private key outside Git and copy it to `/run/kyberm0nk/secrets/windows_unreal_ed25519` with `0600` permissions.
- Use the sandbox SSH config alias `unreal-windows`, which targets the Windows OpenSSH server with `IdentitiesOnly yes` and `BatchMode yes`.
- Treat the Windows node as a privileged executor: give Agent Zero specific tasks and project paths, not broad exploratory host-control prompts.

## Logging

Logs must include timestamps. Tool logs should go under `logs/`, which is ignored by Git.
