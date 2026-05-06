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

## Logging

Logs must include timestamps. Tool logs should go under `logs/`, which is ignored by Git.
