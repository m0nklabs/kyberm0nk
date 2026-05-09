#!/usr/bin/env bash
# KyberM0nk: launch Agent Zero web UI inside the sandbox container.
#
# This wires Guardian as Agent Zero's chat & utility model provider,
# starts run_ui.py on 0.0.0.0:50001, and waits for /health to return 200.
#
# Web UI: http://127.0.0.1:50001 on the host.
set -euo pipefail

cd "$(dirname "$0")/.."

UI_PORT="${AGENT_ZERO_PORT:-50001}"

echo "[agent-zero] ensuring sandbox container is up..."
container_id="$(docker compose ps -q sandbox)"
if [[ -n "${container_id}" ]]; then
    if [[ "$(docker inspect --format '{{.State.Running}}' "${container_id}")" != "true" ]]; then
        docker start "${container_id}" >/dev/null
    fi
else
    docker compose up -d --no-build sandbox >/dev/null
fi

echo "[agent-zero] ensuring config directories exist..."
docker compose exec -T sandbox bash -lc '
set -euo pipefail
mkdir -p /opt/agent-zero/usr/plugins/_model_config
mkdir -p /opt/agent-zero/usr/uploads /a0/usr
if [[ -L /a0/usr/uploads ]]; then
    current_target="$(readlink /a0/usr/uploads)"
    if [[ "${current_target}" != "/opt/agent-zero/usr/uploads" ]]; then
        rm -f /a0/usr/uploads
        ln -s /opt/agent-zero/usr/uploads /a0/usr/uploads
    fi
elif [[ ! -e /a0/usr/uploads ]]; then
    ln -s /opt/agent-zero/usr/uploads /a0/usr/uploads
fi
if [[ -f /config/agent-zero/patches/vision_load.py ]]; then
    cp /config/agent-zero/patches/vision_load.py /opt/agent-zero/tools/vision_load.py
fi
# user-override is config.json (yaml only used for defaults)
cp /config/agent-zero/model_config.json /opt/agent-zero/usr/plugins/_model_config/config.json
# remove any leftover yaml override that the plugin would ignore anyway
rm -f /opt/agent-zero/usr/plugins/_model_config/config.yaml

echo "  config.json in place:"
head -8 /opt/agent-zero/usr/plugins/_model_config/config.json
'

echo "[agent-zero] restoring tracked project templates..."
./scripts/provision_agent_zero_projects.sh

echo "[agent-zero] checking if Agent Zero is already running..."
if docker compose exec -T sandbox bash -lc 'pgrep -f "[r]un_ui.py" >/dev/null 2>&1'; then
    echo "[agent-zero] already running; restart with: $0 stop && $0"
else
    echo "[agent-zero] starting run_ui.py in background (logs: ./logs/agent-zero/web.log)..."
    mkdir -p ./logs/agent-zero
    docker compose exec -d sandbox bash -lc '
cd /opt/agent-zero
mkdir -p /logs/agent-zero
python run_ui.py --dockerized=true --host 0.0.0.0 --port '"$UI_PORT"' </dev/null >/logs/agent-zero/web.log 2>&1
'
fi

echo "[agent-zero] waiting for http://127.0.0.1:${UI_PORT}/api/health ..."
for i in $(seq 1 60); do
    if curl -sSf -m 2 "http://127.0.0.1:${UI_PORT}/api/health" >/dev/null 2>&1; then
        echo "[agent-zero] ✓ alive at http://127.0.0.1:${UI_PORT}"
        echo "[agent-zero] tail -f ./logs/agent-zero/web.log to follow startup"
        exit 0
    fi
    sleep 2
done

echo "[agent-zero] ✗ timed out waiting for /health" >&2
echo "Last 60 log lines:" >&2
tail -60 ./logs/agent-zero/web.log >&2 || true
exit 1
