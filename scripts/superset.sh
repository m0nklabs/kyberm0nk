#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Execute Superset exclusively inside the Docker sandbox.
CONTAINER_NAME="kyberm0nk-sandbox-1"

# Sandbox specific paths
SANDBOX_HOME="/root/.superset"
SANDBOX_PROJECT="/workspace/project"

if [[ -f "$DIR/.env" ]]; then
    set -a
    source "$DIR/.env"
    set +a
fi

if ! docker ps --format "{{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
    echo "Error: Sandbox container ($CONTAINER_NAME) is not running." >&2
    echo "Run 'docker compose up -d sandbox' first." >&2
    exit 1
fi

print_links() {
    printf 'Superset links:\n'
    printf '  Website:       https://superset.sh\n'
    printf '  CLI install:   (Bundled in sandbox container)\n'
}

usage() {
    printf 'Usage: scripts/superset.sh <command> [args...]\n\n'
    printf 'Commands:\n'
    printf '  status              Show sandbox Superset host status\n'
    printf '  start               Start Superset host daemon inside the sandbox\n'
    printf '  login               Run Superset OAuth login in sandbox\n'
    printf '  whoami              Show Superset auth identity in sandbox\n'
    printf '  agents              List Superset agents inside sandbox\n'
    printf '  seed-agents         Add Kyber Guardian-backed agents inside sandbox\n'
    printf '  import-active       Register ACTIVE_PROJECT inside the sandbox Superset\n'
    printf '  passthrough ...     Run any raw Superset CLI command inside sandbox\n'
}

docker_exec() {
    docker exec -it "$CONTAINER_NAME" "$@"
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
        # Note: start runs as daemon inside the container.
        # (It binds port 45553 inside the container).
        docker_exec /usr/local/superset/bin/superset "$command_name" "$@"
        ;;
    login|whoami)
        docker_exec /usr/local/superset/bin/superset auth "$command_name" "$@"
        ;;
    agents)
        docker_exec /usr/local/superset/bin/superset agents list --local --json "$@"
        ;;
    seed-agents)
        docker_exec /usr/local/superset/bin/superset agents list --local --json >/dev/null 2>&1 || true
        # Run the seeder inside the sandbox so preset command paths use container paths.
        docker exec -i "$CONTAINER_NAME" python3 /workspace/project/scripts/seed_superset_agents.py --home "$SANDBOX_HOME" "$@"
        ;;
    import-active)
        # We run the bun tRPC bypass directly INSIDE the sandbox where bun is installed.
        docker exec -i "$CONTAINER_NAME" bash -c "
            export SUPERSET_HOME_DIR='$SANDBOX_HOME'
            export PROJECT_PATH='$SANDBOX_PROJECT'
            export PROJECT_NAME='$(basename "${ACTIVE_PROJECT:-kyberm0nk}")'
            mkdir -p /tmp/superset-trpc-bypass
            cd /tmp/superset-trpc-bypass
            if [ ! -f package.json ]; then
                echo '{}' > package.json
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
        "
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        docker_exec /usr/local/superset/bin/superset "$command_name" "$@"
        ;;
esac
