#!/usr/bin/env bash
set -euo pipefail

remote_user="${VIBEUE_WINDOWS_USER:-ue_agent}"
remote_host="${VIBEUE_WINDOWS_HOST:-192.168.1.245}"
local_port="${VIBEUE_LOCAL_PORT:-56701}"
ssh_key="${VIBEUE_SSH_KEY:-/home/flip/.ssh/kyberm0nk_windows_unreal_ed25519}"
local_url="http://127.0.0.1:${local_port}/mcp"

candidate_remote_ports=()
if [[ -n "${VIBEUE_REMOTE_PORT:-}" ]]; then
    candidate_remote_ports+=("${VIBEUE_REMOTE_PORT}")
fi

if [[ -n "${VIBEUE_REMOTE_PORTS:-}" ]]; then
    read -r -a configured_remote_ports <<< "${VIBEUE_REMOTE_PORTS//,/ }"
    candidate_remote_ports+=("${configured_remote_ports[@]}")
else
    # Prefer the currently used NerveSplat proxy, then its direct server,
    # then the NewNexus proxy/server pair.
    candidate_remote_ports+=(56701 56700 62352 62351)
fi

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

start_tunnel() {
    local remote_port="$1"
    ssh -i "$ssh_key" \
        -o ExitOnForwardFailure=yes \
        -o ServerAliveInterval=30 \
        -o ServerAliveCountMax=3 \
        -f -N \
        -L "${local_port}:127.0.0.1:${remote_port}" \
        "${remote_user}@${remote_host}"
}

pick_remote_port() {
    local -A seen_ports=()
    local remote_port=""

    for remote_port in "${candidate_remote_ports[@]}"; do
        if [[ -z "$remote_port" || -n "${seen_ports[$remote_port]:-}" ]]; then
            continue
        fi
        seen_ports[$remote_port]=1

        recycle_tunnel
        if ! start_tunnel "$remote_port"; then
            continue
        fi

        if is_mcp_healthy "$local_url"; then
            echo "$remote_port"
            return 0
        fi
    done

    recycle_tunnel
    return 1
}

if [[ -n "${VIBEUE_REMOTE_URL:-}" ]]; then
    if ! is_mcp_healthy "${VIBEUE_REMOTE_URL}"; then
        echo "VibeUE MCP endpoint is unreachable: ${VIBEUE_REMOTE_URL}" >&2
        exit 1
    fi
    exec npx -y mcp-remote "${VIBEUE_REMOTE_URL}" --transport http-only --allow-http
fi

selected_remote_port="$(pick_remote_port)" || {
    echo "Failed to find a healthy VibeUE MCP endpoint on ${remote_host}. Tried remote ports: ${candidate_remote_ports[*]}" >&2
    exit 1
}

echo "Using VibeUE MCP remote port ${selected_remote_port} via local port ${local_port}" >&2

exec npx -y mcp-remote "$local_url" --transport http-only --allow-http
