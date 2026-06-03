# Hermes Operator Guide

This guide is for operators running Hermes Gateway in production — starting, stopping, inspecting queue state, and recovering from common issues.

## Hermes Gateway Lifecycle

### Starting Hermes

```bash
cd /home/flip/hermes-agent
./gateway/run.py &
# or use systemd if configured:
systemctl --user start hermes-gateway
```

Gateway registers slash commands at startup and connects to:
- **Guardian proxy** at `http://127.0.0.1:11434/v1`
- **Issue resolution DB** at `~/.hermes/issue_resolution.db`
- **Router** (if enabled) on `127.0.0.1:11442`

### Checking Hermes Status

```bash
# Check if daemon is running
ps aux | grep 'hermes.*run.py' | grep -v grep

# Check Gateway logs
tail -f ~/.hermes/logs/agent.log

# Check error logs if something seems wrong
tail -100 ~/.hermes/logs/errors.log
```

### Stopping Hermes

```bash
pkill -f 'hermes.*run.py'
# or if using systemd:
systemctl --user stop hermes-gateway
```

Always verify the process stopped — if Hermes is mid-Aider-job, wait for it to finish naturally or force-kill after a bounded timeout.

### Restarting Hermes

```bash
pkill -f 'hermes.*run.py'
sleep 5
ps aux | grep hermes | grep -v grep | grep -q . && pkill -9 -f 'hermes.*run.py'
./gateway/run.py &
```

Gateway startup resume restores interrupted `running` rows to `queued` state and re-processes pending work.

## GitHub Issue Resolution Lane

### Slash Commands

Hermes Gateway exposes these slash commands via CLI, Telegram, and webhook:

| Command | Purpose |
|---------|---------|
| `/issue <repo> <number>` | Queue a GitHub issue for resolution |
| `/status <repo>` | Show queue status for a repo |
| `/cancel <repo> <number>` | Cancel a queued or running issue |
| `/retry <repo> <number>` | Retry a failed issue run |
| `/config` | Show current Gateway configuration |
| `/reload` | Hot-reload config files |

### Queuing an Issue Manually

```bash
# Via Hermes CLI
./gateway/run.py /issue cryptotrader 345

# Via Discord/Telegram (if configured)
/issue cryptotrader 345

# Via GitHub webhook (automatic)
# Hermes auto-detects eligible issues and queues them
```

### Triaging an Issue

1. Check if it's eligible (repo allowlist, correct labels)
2. Verify Guardian proxy is up (`http://127.0.0.1:11434/healthz`)
3. Ensure no competing Aider jobs are running (single-flight constraint)
4. Queue via slash command
5. Monitor `agent.log` for queue pick-up

### Useful gh Commands

Quick GitHub inspection from the CLI — pairs well with queue queries:

```bash
# Verify PR state and merge status
gh pr view <number> --json state,mergedAt,title --repo <owner>/<repo>

# Check CI status on a PR
gh pr checks <number> --repo <owner>/<repo>

# Post a quick comment
gh issue comment <number> --body "Manual review: ..." --repo <owner>/<repo>

# Inspect reviewer feedback
gh pr review <number> --repo <owner>/<repo> 2>/dev/null | head -30

# List labels on an issue
gh issue view <number> --json labels --repo <owner>/<repo>
```

## Startup Checklist

Run this before starting Hermes in production:

```bash
# 1. Guardian proxy healthy
curl -sf http://127.0.0.1:11434/healthz || echo "FAIL: Guardian down"

# 2. GitHub token authenticates
gh auth status 2>&1 | grep -q 'Logged in' || echo "FAIL: `gh` not authenticated"

# 3. OpenRouter reachable (if tiered reviewers are enabled)
curl -sf https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY" > /dev/null \
  || echo "WARN: OpenRouter unreachable — cloud reviewers will fail"

# 4. Hermes systemd unit status
systemctl --user is-active hermes-gateway hermes-dashboard 2>/dev/null
# Expected: active active
```

All four checks green → safe to start queueing issues.

## SQLite Queue Inspection

The queue state lives in `~/.hermes/issue_resolution.db`.

### Schema Overview

Inspect what tables exist before querying:

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT name FROM sqlite_master 
WHERE type='table' 
ORDER BY name;
SQL
```

Common tables: `issue_runs`, `master_subissues`, `issue_run_logs`, `run_artifacts`. Column names can be listed:

```bash
sqlite3 ~/.hermes/issue_resolution.db "PRAGMA table_info(issue_runs);"
```

### Check Queue Size

```bash
sqlite3 ~/.hermes/issue_resolution.db "SELECT COUNT(*) FROM issue_runs WHERE status='queued';"
```

### Show Active Runs

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT repo, issue_number, status, attempt_count, updated_at 
FROM issue_runs 
WHERE status IN ('running', 'queued', 'expanded')
ORDER BY updated_at DESC;
SQL
```

### Show Completed / Failed Runs

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT repo, issue_number, status, pr_number, attempt_count, completed_at 
FROM issue_runs 
WHERE status IN ('completed', 'failed')
ORDER BY completed_at DESC 
LIMIT 20;
SQL
```

### Investigate a Stuck Run

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT * FROM issue_runs 
WHERE issue_number=345 AND repo='cryptotrader'
ORDER BY run_number DESC
LIMIT 1;
SQL
```

Look for:
- `status='running'` with old `updated_at` → stuck run
- `status='failed'` with high `attempt_count` → hitting ceiling, manual investigation needed
- `status='failed'` with `next_attempt_at` in future → still in retry window

### Reset a Stuck Run

If Hermes crashed mid-run and left it in `running` state:

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
UPDATE issue_runs 
SET status='queued', attempt_count=attempt_count+1, updated_at=datetime('now')
WHERE repo='cryptotrader' AND issue_number=345 AND status='running';
SQL
```

Then restart Hermes Gateway.

## Guardian Health Check

### Verify Guardian is Reachable

```bash
curl -s http://127.0.0.1:11434/healthz
# Should return: {"status":"ok"}

curl -s http://127.0.0.1:11434/v1/models | head -20
# Lists available model aliases
```

### Guardian is Down

```bash
# Check Guardian proxy status
curl http://127.0.0.1:11434/healthz

# Check Guardian daemon
ps aux | grep -i guardian | grep -v grep

# Restart Guardian if needed
systemctl --user restart guardian  # or direct script
```

If Guardian proxy stays unreachable, Hermes queue will back up with failed runs after max retries.

## Review Loop Controls

### Kyber-Tag Routing

After Hermes opens a PR, reviewer loop posts comments with structured tags:

- `kyber-tag: coding_subagent` → Hermes routes Aider back to fix findings
- `kyber-tag: ready_for_merge` → Hermes merges PR
- `kyber-tag: rerun_reviewer` → Hermes re-runs reviewer

### Force a Review Rerun

```bash
# Manually trigger reviewer on a PR
cd /home/flip/.hermes/scripts
python3 cryptotrader_pr_aider_reviewer_loop.py --pr cryptotrader 567 --force
```

### Cancel a Fix Loop

If Aider is stuck in a review-fix loop (3+ iterations):

1. Post `kyber-tag: review_inconclusive` comment on PR
2. Set issue state to `needs_human_review`
3. Close Hermes queue entry

## Environment Variables Quick Reference

### Core Routing

| Variable | Default | Purpose |
|----------|---------|---------|
| `GUARDIAN_BASE_URL` | `http://127.0.0.1:11434` | Local model proxy |
| `ANTHROPIC_API_KEY` | `local-router` | Gateway auth (if using Claude router) |
| `OPENROUTER_API_KEY` | — | OpenRouter API key for tiered reviewers |
| `GITHUB_TOKEN` | — | GitHub API token for PR/comment operations |

### Claude Code Launcher

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_LOCAL_MODEL` | `qwen3-35b-uncensored` | Default local model |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `85` | Auto-compact trigger threshold (%) |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `8192` | Max tokens per turn |
| `CLAUDE_CODE_SUBAGENT_MODEL` | — | Override for subagent tier models |

### Hermes Agent

| Variable | Default | Purpose |
|----------|---------|---------|
| `HERMES_ISSUE_DECOMPOSE_MODEL` | `qwen3-35b-uncensored` | Epic decomposition model |
| `AIDER_REVIEWER_MODEL` | OpenRouter tier1 | Model for tier1 reviewer |
| `AIDER_CODER_MODEL` | Qwen3/Guardian | Model for code fixes |

## Logging Locations

| Log | Purpose |
|-----|---------|
| `~/.hermes/logs/agent.log` | Gateway main log (commands, queue state) |
| `~/.hermes/logs/errors.log` | Gateway errors (crashes, exceptions) |
| `~/.cache/claudecode/claude-router.log` | Router log (if enabled) |
| `~/llama_cpp_guardian/logs/` | Guardian inference logs |

## Common Issues & Solutions

### Queue is Stuck — No Issues Being Processed

**Symptoms:** Queue count > 0 but nothing happening

**Check:**
1. Hermes process running? `ps aux | grep hermes`
2. Guardian reachable? `curl http://127.0.0.1:11434/healthz`
3. Check errors in `~/.hermes/logs/errors.log`
4. Restart Hermes if needed

### Aider Job Fails with Model Load Error

**Symptoms:** Issue marked `failed` with attempt_count > 1

**Check:**
1. Guardian proxy responding? `curl http://127.0.0.1:11434/v1/models`
2. Model alias configured? Check Guardian logs for load errors
3. Guardian slot available? Hermes enforces single-flight, so queue backs up during active jobs

**Fix:** Wait for current job to finish or restart Guardian if unresponsive.

### Reviewer Loop Hangs

**Symptoms:** PR stays open for hours with no comments

**Check:**
1. Reviewer script running? `ps aux | grep reviewer_loop`
2. Reviewer logs show errors? Check `~/.hermes/scripts/` stderr
3. OpenRouter key valid? Test with `curl https://openrouter.ai/api/v1/models`

**Fix:** Force-restart reviewer with `--force` flag.

### Hermes Can't Create PR

**Symptoms:** Aider finishes work but PR creation fails

**Check:**
1. GitHub token has `repo` scope?
2. Branch name conflicts with existing branch?
3. No merge conflicts with base branch?

**Fix:** Verify GitHub token permissions; delete conflicting branch; run `git status` on worktree.

## Performance Characteristics

### Current Limits

- **Single-flight coder**: Only one Aider job runs at a time (Guardian slot constraint)
- **Queue depth**: Unlimited SQLite rows, but expect 20-30 min per issue
- **Throughput**: ~2-3 issues/hour with full review+fix loop

### Bottlenecks

1. **Guardian slot**: Only one inference request at a time; Hermes queue enforces single-flight
2. **Context size**: 65536 tokens default; avoid 32768 output caps for reliable completion
3. **OpenRouter limits**: Tiered reviewers use cloud API; watch credit spend

## Recovery Procedures

### Recovering from Hermes Crash

1. Check `~/.hermes/logs/agent.log` for crash reason
2. Restart Hermes: `./gateway/run.py &`
3. Hermes auto-resumes `running` → `queued` at startup
4. Monitor next 5 minutes for queue progression

### Recovering Stuck PR

If Hermes opens PR but merge step never completes:

1. Check queue: `SELECT * FROM issue_runs WHERE pr_number=567`
2. If `status='running'` with old timestamp → manual reset needed:
   ```bash
   sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
   UPDATE issue_runs SET status='queued' 
   WHERE pr_number=567 AND repo='cryptotrader';
   SQL
   ```
3. Restart Hermes

### Restoring SQLite DB from Corruption

**Backup strategy (recommended cron):**
```bash
#!/bin/bash
BACKUP_DIR=~/.hermes/backups
mkdir -p "$BACKUP_DIR"
cp ~/.hermes/issue_resolution.db "$BACKUP_DIR/issue_resolution.db.$(date +%Y%m%d)"
# Keep last 7 days
find "$BACKUP_DIR" -name "issue_resolution.db.*" -mtime +7 -delete
```

**Restore:**
```bash
kill -9 $(pgrep -f hermes)
cp ~/.hermes/backups/issue_resolution.db.YYYYMMDD ~/.hermes/issue_resolution.db
./gateway/run.py &
```

## Maintenance

### Cleaning Up Old Runs

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
DELETE FROM issue_runs 
WHERE status='completed' AND completed_at < date('now', '-90 days');
VACUUM;
SQL
```

### Inspecting Sub-Issue Decomposition

```bash
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT parent_issue, child_issue, child_status 
FROM master_subissues 
WHERE parent_issue=100;
SQL
```

### Kanban Sync

Kanban tasks live in `~/.hermes/kanban.db`:

```bash
sqlite3 ~/.hermes/kanban.db "SELECT COUNT(*) FROM kanban_tasks;"
```

Sync script: `~/.hermes/scripts/github_issue_kanban_sync.py`

## Escalation Path

When a queue run fails repeatedly or Hermes behavior is unexpected:

### Record the Incident

Create a local incident file before opening a Kyber issue:

```bash
INCIDENT_DIR=~/.hermes/incidents
mkdir -p "$INCIDENT_DIR"
cat > "$INCIDENT_DIR/$(date +%Y-%m-%d)-cryptotrader-345.txt" <<EOF
Incident: $(date -Iseconds)
Repo: cryptotrader
Issue: 345
Symptom: Queue stuck at attempt 3/3, Aider failing with model timeout
Last log lines:
$(tail -20 ~/.hermes/logs/errors.log)
Recovery attempted: Manual retry via /retry, Guardian restart
EOF
```

### Open a Kyber Issue

```bash
gh issue create \
  --repo flip/kyberm0nk \
  --title "incident: cryptotrader #345 stuck after 3 attempts" \
  --label "incident" \
  --body "See ~/.hermes/incidents/2026-06-03-cryptotrader-345.txt for details"
```

### Severity Classification

| Severity | Criteria | Response |
|----------|----------|----------|
| **P1** | Hermes gateway crashing repeatedly, queue growing with no processing | Immediate: restart, check logs, file incident |
| **P2** | Single issue stuck after max retries, PR orphaned | Within hours: inspect run, manual reset or close |
| **P3** | Non-blocking bug, missing feature in docs or scripts | File issue, next planning cycle |

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) — System structure and workflow
- [ROADMAP.md](ROADMAP.md) — Phases and long-term vision
- [GITHUB_ISSUE_RESOLUTION.md](GITHUB_ISSUE_RESOLUTION.md) — Queue state machine details
- [ISSUE_TO_MERGE_TARGET_STATE.md](ISSUE_TO_MERGE_TARGET_STATE.md) — Target state checklist

