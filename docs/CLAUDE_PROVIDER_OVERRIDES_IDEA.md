# Claude Provider Overrides Idea (Future Option)

Status: proposal only, not active by default.

This note captures a potential future direction: routing Claude Code directly to OpenRouter or DeepSeek-style endpoints via Claude settings, without a local proxy layer.

## Goal

- Reduce token costs during heavy build phases.
- Force cheaper/faster sub-agent models for background scanning work.
- Keep a clear operator-level switch between local-first and cloud-first routes.

## Candidate Settings Shape

Potential target files:

- `~/.claude/settings.json`
- `.claude/settings.local.json`

Candidate environment block (as discussed):

```json
{
  "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
  "ANTHROPIC_AUTH_TOKEN": "YOUR_OPENROUTER_OR_DEEPSEEK_API_KEY",
  "ANTHROPIC_API_KEY": "",
  "ANTHROPIC_MODEL": "deepseek/deepseek-v4-pro",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek/deepseek-v4-pro",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek/deepseek-v4-pro",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek/deepseek-v4-flash",
  "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek/deepseek-v4-flash",
  "CLAUDE_CODE_EFFORT_LEVEL": "max",
  "CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK": "1",
  "DISABLE_TELEMETRY": "1"
}
```

## Important Caveats

1. Keep `ANTHROPIC_API_KEY` explicitly empty when routing through a non-Anthropic endpoint, to avoid mixed-auth confusion.
2. Run `claude /logout` once before first use to clear stale first-party Anthropic sessions.
3. Keep API keys out of repo-tracked files. Use local env or secret stores only.
4. Prefer project-local overrides (`.claude/settings.local.json`) for experiments before changing user-global behavior.
5. Validate model id availability on the target provider before rollout, because provider catalogs change frequently.

## Evaluation Plan (When We Decide To Pilot)

1. Add the overrides in a local-only settings file.
2. Run a short A/B test on one project slice: latency, cost, review quality, and tool-call reliability.
3. Compare against the current `claude-local` + Guardian route.
4. Keep rollback simple: remove override file and return to wrapper defaults.

## Why This Is Not Default Today

- Kyber currently uses a stable local-first operator path (`claude-local` + Guardian).
- A direct cloud route can be useful, but it should be a deliberate mode switch, not an always-on default.
