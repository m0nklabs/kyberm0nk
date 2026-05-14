#!/usr/bin/env bash
set -euo pipefail

remote_user="${VIBEUE_WINDOWS_USER:-mark1}"
remote_host="${VIBEUE_WINDOWS_HOST:-192.168.1.245}"
remote_port="${VIBEUE_REMOTE_PORT:-62351}"
local_port="${VIBEUE_LOCAL_PORT:-56701}"
ssh_key="${VIBEUE_SSH_KEY:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
remote_url="${VIBEUE_REMOTE_URL:-http://127.0.0.1:${local_port}/mcp}"

is_port_open() {
    python3 - "$1" <<'PY'
import socket
import sys
port = int(sys.argv[1])
with socket.socket() as sock:
    sock.settimeout(1)
    try:
        sock.connect(("127.0.0.1", port))
    except OSError:
        raise SystemExit(1)
raise SystemExit(0)
PY
}

is_mcp_healthy() {
    python3 - "$1" <<'PY'
import sys
import urllib.request

url = sys.argv[1]
request = urllib.request.Request(url, headers={"Accept": "text/event-stream"})

try:
    with urllib.request.urlopen(request, timeout=3) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

recycle_tunnel() {
    pkill -f -- "-L ${local_port}:127.0.0.1:" 2>/dev/null || true
}

if is_port_open "$local_port" && ! is_mcp_healthy "$remote_url"; then
    recycle_tunnel
fi

if ! is_port_open "$local_port"; then
    ssh -i "$ssh_key" \
        -o ExitOnForwardFailure=yes \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=3 \
        -f -N \
        -L "${local_port}:127.0.0.1:${remote_port}" \
        "${remote_user}@${remote_host}"
fi

exec npx -y mcp-remote "$remote_url" --transport http-only --allow-http
