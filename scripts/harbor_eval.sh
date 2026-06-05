#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$repo_root/.env" ]]; then
    set -a
    source "$repo_root/.env"
    set +a
fi

if [[ -f "$HOME/.config/claudecode/claude-local.env" ]]; then
    set -a
    source "$HOME/.config/claudecode/claude-local.env"
    set +a
fi

usage() {
    cat <<'EOF'
Usage: scripts/harbor_eval.sh <claude-code|hermes|aider> [harbor run args...]

Run the local Harbor source install against Kyber's framework lanes.

This wrapper is for direct CLI runs, not full Harbor job config files.
If you need `--config`, run Harbor directly from /home/flip/harbor.

Environment overrides:
  HARBOR_DIR                Harbor checkout root (default: /home/flip/harbor)
  HARBOR_ENV_TYPE           Harbor environment type (default: docker)
  HARBOR_TASK_PATH          Default task path (default: $HARBOR_DIR/examples/tasks)
  HARBOR_JOBS_DIR           Output root (default: <kyber>/scratch/harbor-jobs)
    HARBOR_DOCKER_HOST        Host alias visible from Harbor docker env
                                                        (default: docker0 bridge IP on Linux, else host.docker.internal)
  HARBOR_GUARDIAN_MODEL     Shared local Guardian model alias override
  HARBOR_CLAUDE_BASE_URL    Anthropic-compatible base URL for Claude Code
  HARBOR_OPENAI_BASE_URL    OpenAI-compatible base URL for Hermes/Aider
  HARBOR_CLAUDE_MODEL       Claude Code model override
  HARBOR_HERMES_MODEL       Hermes model override
  HARBOR_AIDER_MODEL        Aider model override
  HARBOR_CLAUDE_API_KEY     Claude Code auth override
  HARBOR_HERMES_API_KEY     Hermes auth override
  HARBOR_AIDER_API_KEY      Aider auth override

Examples:
  scripts/harbor_eval.sh claude-code
  scripts/harbor_eval.sh hermes --include-task-name write-file
  scripts/harbor_eval.sh aider --path /home/flip/harbor/examples/tasks
EOF
}

first_nonempty() {
    local name=""
    local value=""
    for name in "$@"; do
        value="${!name:-}"
        if [[ -n "$value" ]]; then
            printf '%s' "$value"
            return 0
        fi
    done
    return 1
}

ensure_provider_prefix() {
    local provider="$1"
    local model="$2"
    if [[ "$model" == */* ]]; then
        printf '%s' "$model"
        return 0
    fi
    printf '%s/%s' "$provider" "$model"
}

resolve_docker_host() {
    local docker_host="${HARBOR_DOCKER_HOST:-}"
    local docker_bridge_ip=""

    if [[ -n "$docker_host" ]]; then
        printf '%s' "$docker_host"
        return 0
    fi

    if [[ "$(uname -s)" == "Linux" ]] && command -v ip >/dev/null 2>&1; then
        docker_bridge_ip="$(ip -4 -o addr show docker0 2>/dev/null | awk '{print $4}' | cut -d/ -f1 | head -n1)"
        if [[ -n "$docker_bridge_ip" ]]; then
            printf '%s' "$docker_bridge_ip"
            return 0
        fi
    fi

    printf 'host.docker.internal'
}

has_config_selector() {
    local arg=""
    for arg in "$@"; do
        case "$arg" in
            --config|-c)
                return 0
                ;;
        esac
    done
    return 1
}

has_dataset_selector() {
    local arg=""
    for arg in "$@"; do
        case "$arg" in
            --path|-p|--dataset|-d|--task|-t)
                return 0
                ;;
        esac
    done
    return 1
}

has_jobs_dir_selector() {
    local arg=""
    for arg in "$@"; do
        case "$arg" in
            --jobs-dir|-o)
                return 0
                ;;
        esac
    done
    return 1
}

has_env_selector() {
    local arg=""
    for arg in "$@"; do
        case "$arg" in
            --env|-e)
                return 0
                ;;
        esac
    done
    return 1
}

has_concurrency_selector() {
    local arg=""
    for arg in "$@"; do
        case "$arg" in
            --n-concurrent|-n)
                return 0
                ;;
        esac
    done
    return 1
}

if [[ $# -lt 1 ]]; then
    usage >&2
    exit 64
fi

agent="$1"
shift

case "$agent" in
    help|-h|--help)
        usage
        exit 0
        ;;
    claude-code|hermes|aider)
        ;;
    *)
        printf 'Unsupported Harbor framework lane: %s\n' "$agent" >&2
        usage >&2
        exit 64
        ;;
esac

if has_config_selector "$@"; then
    printf 'scripts/harbor_eval.sh does not accept Harbor job config files. Run Harbor directly for --config workflows.\n' >&2
    exit 64
fi

harbor_dir="${HARBOR_DIR:-$HOME/harbor}"
harbor_env_type="${HARBOR_ENV_TYPE:-docker}"
docker_host="$(resolve_docker_host)"
guardian_model="${HARBOR_GUARDIAN_MODEL:-${DEFAULT_MODEL:-qwen3-35b-uncensored}}"
task_path="${HARBOR_TASK_PATH:-$harbor_dir/examples/tasks}"
jobs_root="${HARBOR_JOBS_DIR:-$repo_root/scratch/harbor-jobs}"
jobs_dir="$jobs_root/$agent"
claude_base_url="${HARBOR_CLAUDE_BASE_URL:-http://$docker_host:11434}"
openai_base_url="${HARBOR_OPENAI_BASE_URL:-http://$docker_host:11434/v1}"

if [[ ! -d "$harbor_dir" ]]; then
    printf 'Harbor checkout not found: %s\n' "$harbor_dir" >&2
    exit 64
fi

if ! command -v harbor >/dev/null 2>&1; then
    printf 'harbor CLI not found. Install it from source with: cd %s && uv tool install --editable --force .\n' "$harbor_dir" >&2
    exit 127
fi

if ! has_dataset_selector "$@" && [[ ! -d "$task_path" ]]; then
    printf 'Default Harbor task path not found: %s\n' "$task_path" >&2
    exit 64
fi

mkdir -p "$jobs_dir"

cmd=(harbor run --agent "$agent" --yes)

if ! has_env_selector "$@"; then
    cmd+=(--env "$harbor_env_type")
fi

if ! has_jobs_dir_selector "$@"; then
    cmd+=(--jobs-dir "$jobs_dir")
fi

if ! has_concurrency_selector "$@"; then
    cmd+=(--n-concurrent 1)
fi

if ! has_dataset_selector "$@"; then
    cmd+=(--path "$task_path")
fi

if [[ "$harbor_env_type" == "docker" ]]; then
    cmd+=(--allow-agent-host "$docker_host")
fi

case "$agent" in
    claude-code)
        if ! claude_api_key="$(first_nonempty HARBOR_CLAUDE_API_KEY CLAUDECODE_GUARDIAN_API_KEY KYBERM0NK_GUARDIAN_API_KEY ANTHROPIC_API_KEY)"; then
            printf 'No Claude Harbor API key found. Set HARBOR_CLAUDE_API_KEY, CLAUDECODE_GUARDIAN_API_KEY, KYBERM0NK_GUARDIAN_API_KEY, or ANTHROPIC_API_KEY.\n' >&2
            exit 64
        fi
        claude_model="${HARBOR_CLAUDE_MODEL:-${CLAUDE_LOCAL_MODEL:-$guardian_model}}"
        cmd+=(--model "$claude_model")
        cmd+=(--agent-env "ANTHROPIC_BASE_URL=$claude_base_url")
        cmd+=(--agent-env "ANTHROPIC_API_KEY=$claude_api_key")
        ;;
    hermes)
        if ! hermes_api_key="$(first_nonempty HARBOR_HERMES_API_KEY KYBERM0NK_GUARDIAN_API_KEY OPENAI_API_KEY)"; then
            printf 'No Hermes Harbor API key found. Set HARBOR_HERMES_API_KEY, KYBERM0NK_GUARDIAN_API_KEY, or OPENAI_API_KEY.\n' >&2
            exit 64
        fi
        hermes_model_raw="${HARBOR_HERMES_MODEL:-$guardian_model}"
        hermes_model="$(ensure_provider_prefix openai "$hermes_model_raw")"
        cmd+=(--model "$hermes_model")
        cmd+=(--agent-env "OPENAI_API_BASE=$openai_base_url")
        cmd+=(--agent-env "OPENAI_API_KEY=$hermes_api_key")
        ;;
    aider)
        if ! aider_api_key="$(first_nonempty HARBOR_AIDER_API_KEY AIDER_GUARDIAN_API_KEY KYBERM0NK_GUARDIAN_API_KEY OPENAI_API_KEY)"; then
            printf 'No Aider Harbor API key found. Set HARBOR_AIDER_API_KEY, AIDER_GUARDIAN_API_KEY, KYBERM0NK_GUARDIAN_API_KEY, or OPENAI_API_KEY.\n' >&2
            exit 64
        fi
        aider_model_raw="${HARBOR_AIDER_MODEL:-${AIDER_LOCAL_MODEL:-$guardian_model}}"
        aider_model="$(ensure_provider_prefix openai "$aider_model_raw")"
        cmd+=(--model "$aider_model")
        cmd+=(--agent-env "OPENAI_API_BASE=$openai_base_url")
        cmd+=(--agent-env "OPENAI_API_KEY=$aider_api_key")
        ;;
esac

printf '[%s] Harbor %s evaluation starting\n' "$(date -Iseconds)" "$agent"
printf '  checkout: %s\n' "$harbor_dir"
printf '  jobs dir: %s\n' "$jobs_dir"

cd "$harbor_dir"
exec "${cmd[@]}" "$@"