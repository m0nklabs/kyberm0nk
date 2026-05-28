# Automated GitHub Issue Resolution

Kyber's issue-resolution lane is implemented in Hermes Gateway as `/issue`.
It uses only the active stack: Hermes, Aider, Guardian, GitHub CLI, SQLite, and
OpenRouter.

## Manual Trigger

```bash
/issue m0nklabs/cryptotrader 10 --workdir /home/flip/cryptotrader
```

The gateway schedules the lane in the background and posts Telegram status
updates for the local coder start, PR creation, reviewer start, and reviewer
completion.

Local coder execution is strict single-flight. If another issue is already in
the local Aider/Guardian lane, the new run stays queued in SQLite until the
current run finishes.

## Master Epic Trigger

Hermes treats an issue as a Master Epic when either condition is true:

- The issue has the `master-plan` label.
- The issue body starts with `# Master Project Plan`.

For Master Epics, Hermes asks Guardian to decompose the plan into ordered atomic
tasks, creates one GitHub sub-issue per task, writes `Part of Master Issue #X` in
each sub-issue body, and queues those sub-issues sequentially through the same
`/issue` lane.

Example master issue body:

```markdown
# Master Project Plan

## Goal
Build the first production-ready issue-resolution automation lane.

## Requirements
- Add persistent queue state.
- Add a local Aider single-flight lock.
- Create PRs automatically.
- Run cloud review after local code generation.
```

## Webhook Trigger

Configure the Hermes `webhook` platform with a route that uses the built-in
automation mode:

```yaml
platforms:
  webhook:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8644
      routes:
        github-issues:
          secret: "replace-with-github-webhook-secret"
          events: ["issues"]
          automation: github_issue_resolution
          deliver: telegram
```

GitHub `issues` webhook payloads are converted into `/issue --repo owner/name
--issue N`. Pull-request-shaped issue payloads are ignored.

## Aider Roles

Local coder:

```bash
OPENAI_API_BASE=http://127.0.0.1:11434/v1 \
OPENAI_API_KEY=$AIDER_GUARDIAN_API_KEY \
/home/flip/aider/.venv/bin/aider --model openai/qwen3-35b-uncensored --yes --no-gitignore --message "$PROMPT"
```

Cloud reviewer:

```bash
OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
OPENAI_API_KEY=$OPENROUTER_API_KEY \
/home/flip/aider/.venv/bin/aider --model openrouter/deepseek/deepseek-v4-flash --cache-prompts --no-auto-commits --yes --no-gitignore --message "$PROMPT"
```

## Current Scope

- Creates/checks out an `issue/<number>-<slug>` branch.
- Detects Master Epics via `master-plan` label or `# Master Project Plan` body.
- Decomposes Master Epics through Guardian.
- Creates sub-issues with `Part of Master Issue #X` references.
- Queues issue runs in SQLite at `~/.hermes/issue_resolution.db`.
- Resets interrupted `running` rows to `queued` on gateway startup.
- Processes local coder work through a strict single-flight FIFO worker.
- Runs local Aider against Guardian.
- Pushes the branch.
- Opens or finds a GitHub PR.
- Runs cloud Aider reviewer against OpenRouter.
- Posts reviewer feedback as an inline PR comment when a diff anchor is found,
  otherwise as a normal PR review comment.

## Next Hardening

- Add per-repo allowlists and richer concurrency controls for cloud review.
- Add cancellation and retry controls.
- Add richer reviewer output parsing for multiple inline comments.
- Add duplicate prevention for crash windows between `gh issue create` and state write.

## SQLite Inspection

```bash
sqlite3 ~/.hermes/issue_resolution.db \
  'SELECT id, repo, issue_number, run_type, status, parent_run_id, pr_number FROM issue_runs ORDER BY id;'
```