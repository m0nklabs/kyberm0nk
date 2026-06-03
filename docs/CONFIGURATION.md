# Configuration Reference

All environment variables used across KyberM0nk stack, organized by component.

## Claude Code Launchers

Launchers live in `~/.local/bin/`: `claude-local`, `claude-online`, `claude-gateway`.

### Core Routing

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_LOCAL_MODEL` | `qwen3.6-35b-uncensored` | Default model for `claude-local` |
| `CLAUDE_ONLINE_MODEL` | `deepseek/deepseek-v4-pro` | Default model for `claude-online` |
| `CLAUDE_GATEWAY_MODEL` | `claude-local-qwen3.6-35b` | Default model for `claude-gateway` |
| `GUARDIAN_BASE_URL` | `http://127.0.0.1:11434` | Guardian proxy endpoint |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api` | OpenRouter API endpoint |
| `CLAUDE_ROUTER_HOST` | `127.0.0.1` | Claude router host |
| `CLAUDE_ROUTER_PORT` | `11442` | Claude router port |

### Claude Code Behavior

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `85` | Auto-compact trigger threshold (%) |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `8192` | Max tokens per turn |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | Effort level for responses |
| `CLAUDE_CODE_SUBAGENT_MODEL` | — | Override for subagent tier models |
| `CLAUDE_CODE_ATTRIBUTION_HEADER` | `0` | Disable attribution header |
| `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK` | `1` | Skip fast mode org check |
| `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY` | `1` | Enable gateway model discovery |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | `1` | Disable experimental betas |
| `CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK` | `1` | Disable non-streaming fallback |
| `ENABLE_PROMPT_CACHING_1H` | `1` | Enable 1-hour prompt caching |

### Tier Model Aliases

Claude Code uses three tier aliases (sonnet/opus/haiku) that map to actual models:

**Local tier (claude-local):**

| Variable | Default |
|----------|---------|
| `CLAUDE_LOCAL_SONNET_MODEL` | `qwen3.6-35b-uncensored` |
| `CLAUDE_LOCAL_OPUS_MODEL` | `gemma4-31b-uncensored` |
| `CLAUDE_LOCAL_HAIKU_MODEL` | `gemma4-e4b` |
| `CLAUDE_LOCAL_SONNET_MODEL_NAME` | `Qwen3.6 35B Local` |
| `CLAUDE_LOCAL_OPUS_MODEL_NAME` | `Gemma4 31B Local` |
| `CLAUDE_LOCAL_HAIKU_MODEL_NAME` | `Gemma4 E4B Local` |

**Online tier (claude-online):**

| Variable | Default |
|----------|---------|
| `CLAUDE_ONLINE_SONNET_MODEL` | `deepseek/deepseek-v4-pro` |
| `CLAUDE_ONLINE_OPUS_MODEL` | `deepseek/deepseek-v4-pro` |
| `CLAUDE_ONLINE_HAIKU_MODEL` | `deepseek/deepseek-v4-flash` |
| `CLAUDE_ONLINE_SONNET_MODEL_NAME` | `OpenRouter DeepSeek V4 Pro` |
| `CLAUDE_ONLINE_OPUS_MODEL_NAME` | `OpenRouter DeepSeek V4 Pro` |
| `CLAUDE_ONLINE_HAIKU_MODEL_NAME` | `OpenRouter DeepSeek V4 Flash` |

**Gateway tier (claude-gateway):**

| Variable | Default |
|----------|---------|
| `CLAUDE_GATEWAY_SONNET_MODEL` | `claude-local-qwen3.6-35b` |
| `CLAUDE_GATEWAY_OPUS_MODEL` | `claude-online-opus-4-7` |
| `CLAUDE_GATEWAY_HAIKU_MODEL` | `claude-local-gemma4-e4b` |
| `CLAUDE_GATEWAY_SONNET_MODEL_NAME` | `Local Qwen3.6 35B` |
| `CLAUDE_GATEWAY_OPUS_MODEL_NAME` | `OpenRouter Opus 4.7` |
| `CLAUDE_GATEWAY_HAIKU_MODEL_NAME` | `Local Gemma4 E4B` |

### Authentication

| Variable | Purpose | Source |
|----------|---------|--------|
| `CLAUDECODE_GUARDIAN_API_KEY` | Guardian API key | `~/.config/claudecode/claude-local.env` |
| `OPENROUTER_API_KEY` | OpenRouter API key | `~/.secrets/keys/openrouter.key` or env |
| `GITHUB_TOKEN` | GitHub API token | `~/.secrets/kyberm0nk_github_token` or env |
| `GH_TOKEN` | GitHub CLI token (alias) | Falls back to `GITHUB_TOKEN` |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub PAT (alias) | Falls back to `GITHUB_TOKEN` |
| `CLAUDE_ROUTER_API_KEY` | Claude router auth | Default: `local-router` |

## Hermes Gateway

### Issue Resolution

| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_HOME` | `~/.hermes` | Hermes state directory |
| `HERMES_ISSUE_WORKDIR` | — | Override workdir for issues |
| `HERMES_ISSUE_REPO` | — | Default repo for `/issue` command |
| `HERMES_ISSUE_DECOMPOSE_MODEL` | `qwen3-35b-uncensored` | Model for epic decomposition |
| `HERMES_ISSUE_AUTO_MERGE_ENABLED` | `0` | Enable auto-merge for low-risk PRs |
| `HERMES_ISSUE_ALLOWED_REPOS` | — | CSV of repos allowed in queue |
| `HERMES_MANAGED_REPOS` | — | CSV of repos Hermes manages |
| `HERMES_ISSUE_ENV_FILE` | — | Path to env file with secrets |

### Aider Execution

| Variable | Default | Purpose |
|----------|---------|---------|
| `AIDER_BIN` | `~/aider/.venv/bin/aider` or shell `$PATH` | Aider binary path |
| `AIDER_MODEL` | Guardian `qwen3-35b-uncensored` | Default Aider model |
| `AIDER_LOCAL_MODEL` | — | Override for local Aider runs |
| `AIDER_CLOUD_REVIEW_MODEL` | Tier-specific | Cloud model for reviewers |
| `AIDER_GUARDIAN_API_KEY` | Guardian key | Auth for Guardian proxy |
| `GUARDIAN_BASE_URL` | `http://127.0.0.1:11434/v1` | Guardian OpenAI endpoint |
| `KYBERM0NK_GUARDIAN_API_KEY` | Fallback | Alternative Guardian key var |
| `GUARDIAN_API_KEY` | Fallback | Alternative Guardian key var |

### Reviewer Loop

| Variable | Default | Purpose |
|----------|---------|---------|
| `PR_CODER_MODEL` | `openrouter/deepseek/deepseek-v4-flash` | Coder tier model |
| `PR_REVIEWER_TIER1_MODEL` | Qwen3 local | Tier1 reviewer |
| `PR_REVIEWER_TIER2_MODEL` | DeepSeek V4 Pro | Tier2 reviewer |
| `PR_REVIEWER_TIER3_MODEL` | OpenRouter premium | Tier3 adversarial |

## Guardian Proxy

Guardian config lives in `~/.config/llama_cpp_guardian/config.yaml` and `models.yaml`.

### Runtime

| Variable | Default | Purpose |
|----------|---------|---------|
| `GUARDIAN_PORT` | `11434` | Guardian proxy port |
| `GUARDIAN_BACKEND_PORT` | `11440` | Guardian backend port |
| `GUARDIAN_CONTEXT` | `8192` | Default context window |

**Note:** GPU offload, VRAM, tensor split, and backend llama-server tuning live inside Guardian — Kyber calls only the proxy endpoint. See Guardian docs for those settings.

### Model Aliases

Configured in `~/.config/llama_cpp_guardian/models.yaml`:

- `qwen3-35b-uncensored` → Qwen3 35B GGUF
- `gemma4-31b-uncensored` → Gemma4 31B GGUF
- `gemma4-e4b` → Gemma4 E4B GGUF
- `claude-local-qwen3.6-35b` → Qwen3.6 35B (newer)

**Note:** Never edit `models.yaml` unless explicitly requested by operator.

## CryptoTrader Scripts

Scripts in `~/.hermes/scripts/` use these:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GITHUB_TOKEN` | from `~/.secrets/` | GitHub API auth |
| `OPENROUTER_API_KEY` | from `~/.secrets/` | Tiered reviewer models |
| `AIDER_BIN` | auto-detected | Aider binary |

## File Locations

| Path | Purpose |
|------|---------|
| `~/.config/claudecode/claude-local.env` | Claude Code launcher config |
| `~/.secrets/kyberm0nk_github_token` | GitHub token |
| `~/.secrets/keys/openrouter.key` | OpenRouter API key |
| `~/.hermes/issue_resolution.db` | Hermes queue SQLite |
| `~/.hermes/kanban.db` | Kanban task database |
| `~/.hermes/logs/agent.log` | Gateway main log |
| `~/.hermes/logs/errors.log` | Gateway errors |
| `~/.cache/claudecode/claude-router.log` | Router log |
| `~/llama_cpp_guardian/logs/` | Guardian inference logs |

## Example .env Setup

Create `~/.config/claudecode/claude-local.env`:

```bash
# Guardian
export CLAUDECODE_GUARDIAN_API_KEY="your-guardian-key"
export GUARDIAN_BASE_URL="http://127.0.0.1:11434"

# OpenRouter (for online/gateway)
export OPENROUTER_API_KEY_FILE="$HOME/.secrets/keys/openrouter.key"

# GitHub
export GITHUB_TOKEN_FILE="$HOME/.secrets/kyberm0nk_github_token"

# Claude Code behavior
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=85
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192
export CLAUDE_LOCAL_MODEL="qwen3.6-35b-uncensored"
```

## See Also

- [OPERATOR_GUIDE.md](OPERATOR_GUIDE.md) — Running Hermes in production
- [ARCHITECTURE.md](ARCHITECTURE.md) — System structure
- [LOCAL_AGENT_MODEL_SETTINGS.md](LOCAL_AGENT_MODEL_SETTINGS.md) — Model budgets

