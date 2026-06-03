# Incident Response Guide

Procedures for handling production incidents in Hermes Gateway and KyberM0nk components.

## Severity Classification

| Severity | Criteria | Response Time | Escalation |
|----------|----------|---------------|------------|
| **P1 — Critical** | Hermes repeatedly crashing, queue blocked, no processing possible | Immediate | File Kyber issue with `incident` label |
| **P2 — High** | Single issue stuck, PR orphaned, retry limit hit | Within 2 hours | Inspect run, manual reset or close |
| **P3 — Medium** | Non-blocking bug, missing doc, slow performance | Within 1 day | File Kyber issue, next planning cycle |
| **P4 — Low** | Cosmetic issue, minor doc gap, improvement suggestion | As capacity allows | File Kyber issue |

---

## P1: Hermes Gateway Crashing

**Symptoms:**

- `systemctl --user status hermes-gateway` shows `activating (start)` repeatedly
- `~/.hermes/logs/errors.log` has recent crash tracebacks
- Queue count growing but nothing processing

**Runbook:**

```bash
# 1. Confirm crash loop
systemctl --user status hermes-gateway
journalctl --user -u hermes-gateway -n 50 --no-pager

# 2. Capture error context
tail -100 ~/.hermes/logs/errors.log > ~/hermes-crash-$(date +%Y%m%d).log

# 3. Stop crash loop
systemctl --user stop hermes-gateway

# 4. Inspect queue state
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT repo, issue_number, status, attempt_count, updated_at
FROM issue_runs
WHERE status IN ('running', 'queued')
ORDER BY updated_at DESC;
SQL

# 5. Record incident
mkdir -p ~/.hermes/incidents
cat > ~/.hermes/incidents/$(date +%Y-%m-%d)-gateway-crash.txt <<EOF
Incident: $(date -Iseconds)
Symptom: Gateway crash loop
Queue at crash: $(sqlite3 ~/.hermes/issue_resolution.db "SELECT COUNT(*) FROM issue_runs WHERE status IN ('running','queued');")
Last errors (from errors.log):
$(tail -30 ~/.hermes/logs/errors.log | sed 's/^/  /')
EOF

# 6. File Kyber issue
gh issue create \
  --repo flip/kyberm0nk \
  --title "P1: $(date +%Y-%m-%d) Hermes gateway crash loop" \
  --label "incident,p1" \
  --body "See ~/.hermes/incidents/$(date +%Y-%m-%d)-gateway-crash.txt for traceback. Queue blocked."
```

**Recovery:**

After root cause identified and fixed:

```bash
# Start gateway
systemctl --user start hermes-gateway

# Watch first 5 minutes
journalctl --user -u hermes-gateway -f

# Verify queue resumes
sqlite3 ~/.hermes/issue_resolution.db "SELECT COUNT(*) FROM issue_runs WHERE status='running';"
```

---

## P2: Issue Stuck After Max Retries

**Symptoms:**

- Issue in queue with `status='failed'` and `attempt_count` at ceiling (typically 3)
- PR created but never merged or closed
- Hermes no longer picking up this issue

**Runbook:**

```bash
# 1. Inspect run history
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT run_number, status, attempt_count, pr_number, error_message, updated_at
FROM issue_runs
WHERE repo='<repo>' AND issue_number=<number>
ORDER BY run_number DESC;
SQL

# 2. Check error details
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
SELECT error_message, completed_at
FROM issue_runs
WHERE repo='<repo>' AND issue_number=<number>
ORDER BY run_number DESC
LIMIT 1;
SQL

# 3. If PR orphaned, manually close or merge
gh pr view <pr_number> --json state,title --repo <owner>/<repo>

# 4. If issue should be retried (transient error)
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
UPDATE issue_runs
SET status='queued', attempt_count=0, error_message=NULL
WHERE repo='<repo>' AND issue_number=<number>;
SQL

# 5. Or mark as needs_human_review
gh issue edit <number> \
  --repo <owner>/<repo> \
  --add-label "needs_human_review" \
  --body "Hermes exhausted retries ($(date -Iseconds)). See error details in queue."
```

---

## P2: OpenRouter API Down

**Symptoms:**

- Reviewer loop posts errors: `"OpenRouter API unavailable"`
- OpenRouter tier models unreachable: `curl https://openrouter.ai/api/v1/models` times out
- PRs staying open with no reviewer comments

**Runbook:**

```bash
# 1. Confirm OpenRouter status
curl -sf https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  > /dev/null && echo "OK" || echo "FAIL: OpenRouter unreachable"

# 2. Check OpenRouter status page
# https://status.openrouter.ai (browser)

# 3. If extended outage, pause reviewer loop
# Comment on affected PRs:
gh pr comment <number> \
  --repo <owner>/<repo> \
  --body "Reviewer loop paused: OpenRouter API unavailable. Will resume when service restored."

# 4. Optionally: route to local Guardian model
# Edit HERMES_ISSUE_DECOMPOSE_MODEL to a local Guardian alias
export HERMES_ISSUE_DECOMPOSE_MODEL="qwen3-35b-uncensored"
systemctl --user restart hermes-gateway
```

**Recovery:**

Once OpenRouter is back:

```bash
# Resume reviewer
systemctl --user restart hermes-gateway

# Re-trigger stuck reviews
cd ~/.hermes/scripts
python3 cryptotrader_pr_aider_reviewer_loop.py --pr <repo> <pr_number> --force
```

---

## P2: GitHub Rate Limit

**Symptoms:**

- Hermes logs: `"GitHub API rate limit exceeded"` or HTTP 429 errors
- PR creation or issue commenting fails
- `gh` commands return rate limit errors

**Runbook:**

```bash
# 1. Check current rate limit
gh api rate_limit --jq '.rate | "Used: \(.used) / \(.limit) — Resets: \(.reset | strftime("%H:%M UTC"))"'

# 2. Identify which endpoint is hitting the limit (issues, pulls, etc.)
gh api rate_limit --jq '.resources | to_entries[] | select(.value.used > (.value.limit * 0.9)) | .key'

# 3. Pause queueing new issues
# Don't queue new issues until rate limit resets

# 4. For critical issues, use PAT with higher limit if available
export GITHUB_TOKEN="<personal-access-token-with-higher-limit>"
```

**Prevention:**

- Cache `gh` command outputs where possible
- Use bulk API calls (`gh pr list` once, not per-PR)
- Consider GitHub App auth for higher limits

---

## P2: SQLite Database Corruption

**Symptoms:**

- `sqlite3` commands fail: `"database disk image is malformed"`
- Hermes logs: `"sqlite3.OperationalError: database is locked"` or corruption errors
- Queue operations fail silently

**Runbook:**

```bash
# 1. Confirm corruption
sqlite3 ~/.hermes/issue_resolution.db "PRAGMA integrity_check;"

# 2. Stop Hermes
systemctl --user stop hermes-gateway

# 3. Check for backup
ls -lh ~/.hermes/backups/issue_resolution.db.* 2>/dev/null
# If recent backup exists:

# 4. Restore from backup
BACKUP=$(ls -t ~/.hermes/backups/issue_resolution.db.* | head -1)
cp "$BACKUP" ~/.hermes/issue_resolution.db

# 5. Verify restored DB
sqlite3 ~/.hermes/issue_resolution.db "PRAGMA integrity_check;"
# Expected: "ok"

# 6. Restart Hermes
systemctl --user start hermes-gateway
```

**If no backup:**

```bash
# Attempt recovery (may lose some data)
sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
.output recovered.sql
.dump
SQL

# Create fresh DB and re-import
mv ~/.hermes/issue_resolution.db ~/.hermes/issue_resolution.db.corrupt
sqlite3 ~/.hermes/issue_resolution.db < recovered.sql

# Verify
sqlite3 ~/.hermes/issue_resolution.db "PRAGMA integrity_check;"
```

---

## P3: Guardian Proxy Unreachable

**Symptoms:**

- `curl http://127.0.0.1:11434/healthz` times out or fails
- Hermes logs: `"Guardian proxy unavailable"`
- No model inference possible

**Note:** This is Guardian's operational concern. Kyber only calls the proxy endpoint.

**Runbook:**

```bash
# 1. Confirm Guardian status
curl -sf http://127.0.0.1:11434/healthz && echo "OK" || echo "FAIL"

# 2. Check Guardian daemon
ps aux | grep -i guardian | grep -v grep

# 3. Restart Guardian (if you manage it)
systemctl --user restart guardian  # or direct script

# 4. Pause Hermes until Guardian returns
systemctl --user stop hermes-gateway

# 5. Resume when Guardian is back
systemctl --user start hermes-gateway
```

---

## Recording Incidents

Always create a local incident file before opening a Kyber issue:

```bash
INCIDENT_DIR=~/.hermes/incidents
mkdir -p "$INCIDENT_DIR"
cat > "$INCIDENT_DIR/$(date +%Y-%m-%d)-<repo>-<issue>.txt" <<EOF
Incident: $(date -Iseconds)
Repo: <repo>
Issue: <number>
Severity: P<P1/P2/P3/P4>
Symptom: <brief description>
Queue depth at incident: $(sqlite3 ~/.hermes/issue_resolution.db "SELECT COUNT(*) FROM issue_runs WHERE status IN ('running','queued');")
Last log lines:
$(tail -20 ~/.hermes/logs/errors.log | sed 's/^/  /')
Recovery attempted: <what you tried>
EOF
```

Then file a Kyber issue:

```bash
gh issue create \
  --repo flip/kyberm0nk \
  --title "P<severity>: $(date +%Y-%m-%d) <brief description>" \
  --label "incident,p<severity>" \
  --body "See ~/.hermes/incidents/$(date +%Y-%m-%d)-<repo>-<issue>.txt for details"
```

---

## See Also

- [OPERATOR_GUIDE.md](OPERATOR_GUIDE.md) — Production runtime procedures and queue management
- [TESTING.md](TESTING.md) — Validation scripts and pass/fail criteria
- [BACKUP.md](BACKUP.md) — Backup strategies and restore procedures
- [ARCHITECTURE.md](ARCHITECTURE.md) — System structure for understanding component interactions
