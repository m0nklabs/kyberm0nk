#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUPERSET_ROOT="${SUPERSET_ROOT:-${HOME}/superset}"
SUPERSET_HOME_DIR="${SUPERSET_HOME_DIR:-${HOME}/.superset}"
SUPERSET_PROJECT="${ACTIVE_PROJECT:-${DIR}}"

if [[ -z "${SUPERSET_BIN:-}" ]]; then
    if [[ -x "${SUPERSET_ROOT}/packages/cli/dist/superset-linux-x64/bin/superset" ]]; then
        SUPERSET_BIN="${SUPERSET_ROOT}/packages/cli/dist/superset-linux-x64/bin/superset"
    else
        SUPERSET_BIN="${SUPERSET_ROOT}/bin/superset"
    fi
fi

if [[ -f "$DIR/.env" ]]; then
    set -a
    source "$DIR/.env"
    set +a
fi

if [[ -n "${ACTIVE_PROJECT:-}" ]]; then
    SUPERSET_PROJECT="${ACTIVE_PROJECT}"
fi

print_links() {
    printf 'Superset links:\n'
    printf '  Website:       https://superset.sh\n'
    printf '  Host checkout: %s\n' "$SUPERSET_ROOT"
    printf '  Home dir:      %s\n' "$SUPERSET_HOME_DIR"
    printf '  Bootstrap:     scripts/superset_bootstrap.sh\n'
}

usage() {
    printf 'Usage: scripts/superset.sh <command> [args...]\n\n'
    printf 'Commands:\n'
    printf '  status              Show host-native Superset status\n'
    printf '  start               Start the host-native Superset daemon\n'
    printf '  login               Run Superset OAuth login on the host\n'
    printf '  whoami              Show Superset auth identity on the host\n'
    printf '  agents              List Superset agents on the host\n'
    printf '  seed-agents         Add Kyber Guardian-backed agents on the host\n'
    printf '  import-active       Register ACTIVE_PROJECT with host-native Superset\n'
    printf '  passthrough ...     Run any raw host-native Superset CLI command\n'
}

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'Error: required command is missing: %s\n' "$1" >&2
        exit 1
    fi
}

ensure_superset_bin() {
    if [[ ! -x "$SUPERSET_BIN" ]]; then
        printf 'Error: Superset CLI bundle is missing at %s.\n' "$SUPERSET_BIN" >&2
        printf 'Run scripts/superset_bootstrap.sh or set SUPERSET_ROOT/SUPERSET_BIN explicitly.\n' >&2
        exit 1
    fi
}

run_superset() {
    ensure_superset_bin
    env SUPERSET_HOME_DIR="$SUPERSET_HOME_DIR" "$SUPERSET_BIN" "$@"
}

command_name="${1:-}"
if [[ -z "$command_name" ]]; then
    usage
    exit 64
fi
shift || true

case "$command_name" in
    link|bin)
        print_links
        ;;
    status|start|passthrough)
        run_superset "$command_name" "$@"
        ;;
    login|whoami)
        run_superset auth "$command_name" "$@"
        ;;
    agents)
        run_superset agents list --local --json "$@"
        ;;
    seed-agents)
        require_command python3
        run_superset agents list --local --json >/dev/null 2>&1 || true
        python3 "$DIR/scripts/seed_superset_agents.py" --home "$SUPERSET_HOME_DIR" "$@"
        ;;
    import-active)
        require_command bun
        export SUPERSET_HOME_DIR="$SUPERSET_HOME_DIR"
        export PROJECT_PATH="$SUPERSET_PROJECT"
        export PROJECT_NAME="$(basename "${SUPERSET_PROJECT}")"
        mkdir -p /tmp/superset-trpc-bypass
        cd /tmp/superset-trpc-bypass
        if [[ ! -f package.json ]]; then
            printf '{}\n' > package.json
            bun add @trpc/client superjson >/dev/null 2>&1
        fi
        bun -e '
                import { existsSync, readFileSync, readdirSync } from \"node:fs\";
                import { join } from \"node:path\";
                import { createTRPCClient, httpBatchLink } from \"@trpc/client\";
                import SuperJSON from \"superjson\";

                const home = process.env.SUPERSET_HOME_DIR;
                const repoPath = process.env.PROJECT_PATH;
                const name = process.env.PROJECT_NAME;

                const hostRoot = join(home, \"host\");
                const manifests = existsSync(hostRoot)
                    ? readdirSync(hostRoot, { withFileTypes: true })
                        .filter((entry) => entry.isDirectory())
                        .map((entry) => join(hostRoot, entry.name, \"manifest.json\"))
                        .filter((path) => existsSync(path))
                        .map((path) => JSON.parse(readFileSync(path, \"utf8\")))
                        .filter((manifest) => manifest.endpoint && manifest.authToken)
                        .sort((left, right) => (right.startedAt ?? 0) - (left.startedAt ?? 0))
                    : [];

                const manifest = manifests[0];
                if (!manifest) {
                    console.error(\"Manifest missing. Try: scripts/superset.sh start\");
                    process.exit(1);
                }

                const client = createTRPCClient({
                    links: [
                        httpBatchLink({
                            url: \`\${manifest.endpoint}/trpc\`,
                            transformer: SuperJSON,
                            headers: { Authorization: \`Bearer \${manifest.authToken}\` },
                        }),
                    ],
                });

                const discovered = await client.project.findByPath.query({ repoPath });
                const existing = discovered.candidates?.find((candidate) => candidate.source === \"local-path\") ?? discovered.candidates?.[0];

                if (existing) {
                    const setup = await client.project.setup.mutate({
                        projectId: existing.id,
                        mode: { kind: \"import\", repoPath, allowRelocate: false },
                    });
                    console.log(JSON.stringify({ reused: true, projectId: existing.id, ...setup }, null, 2));
                } else {
                    const created = await client.project.create.mutate({
                        name,
                        mode: { kind: \"importLocal\", repoPath },
                    });
                    console.log(JSON.stringify({ reused: false, ...created }, null, 2));
                }
            '
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        run_superset "$command_name" "$@"
        ;;
esac
