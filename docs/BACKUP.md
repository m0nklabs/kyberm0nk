# Backup and Recovery Guide

Procedures for backing up KyberM0nk state and recovering from data loss.

## What to Back Up

### Critical (queue state and secrets)

| Path | Purpose | Size |
|------|---------|------|
| `~/.hermes/issue_resolution.db` | Hermes issue queue and run history | ~32K |
| `~/.hermes/kanban.db` | Kanban task tracking | ~104K |
| `~/.config/claudecode/claude-local.env` | Claude Code launcher config | ~2K |
| `~/.config/claudecode/claude-openrouter.env` | OpenRouter launcher config | ~309B |
| `~/.secrets/kyberm0nk_github_token` | GitHub API token | ~41B |
| `~/.secrets/keys/openrouter.key` | OpenRouter API key | varies |

### Optional (large state, logs)

| Path | Purpose | Size |
|------|---------|------|
| `~/.hermes/state.db` | Extended Hermes state | ~336M |
| `~/.hermes/logs/` | Gateway and error logs | ~18M |
| `~/_cpp_guardian/config.yaml` | Guardian proxy config | ~1K |
| `~/_cpp_guardian/models.yaml` | Guardian model aliases | ~1K |

**Note:** Guardian config is backed up separately from Kyber — Guardian owns its own lifecycle.

### Not Backed Up (by design)

- `~/.hermes/hermes-agent.db` — empty placeholder
- Git repos (managed by GitHub)
- Docker images (rebuild from Dockerfiles)
- Virtual environments (recreate with `pip install`)

---

## Automated Backup Script

Create `~/.hermes/scripts/backup_kyber_state.sh`:

```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR=~/.hermes/backups
DATE=$(date +%Y%m%d)
BACKUP_DIR_DATE="$BACKUP_DIR/$DATE"

mkdir -p "$BACKUP_DIR_DATE"

echo "Backing up Kyber state to $BACKUP_DIR_DATE"

# 1. Databases (critical)
cp ~/.hermes/issue_resolution.db "$BACKUP_DIR_DATE/"
cp ~/.hermes/kanban.db "$BACKUP_DIR_DATE/"

# 2. Secrets (critical)
mkdir -p "$BACKUP_DIR_DATE/secrets"
cp ~/.config/claudecode/*.env "$BACKUP_DIR_DATE/secrets/" 2>/dev/null || true
cp ~/.secrets/kyberm0nk_github_token "$BACKUP_DIR_DATE/secrets/" 2>/dev/null || true
cp -r ~/.secrets/keys/ "$BACKUP_DIR_DATE/secrets/" 2>/dev/null || true

# 3. Guardian config (optional, but useful)
mkdir -p "$BACKUP_DIR_DATE/guardian"
cp ~/llama_cpp_guardian/config.yaml "$BACKUP_DIR_DATE/guardian/" 2>/dev/null || true
cp ~/llama_cpp_guardian/models.yaml "$BACKUP_DIR_DATE/guardian/" 2>/dev/null || true

# 4. Rotate old backups (keep last 7 days)
find "$BACKUP_DIR" -maxdepth 1 -type d -name "[0-9]*" -mtime +7 -exec rm -rf {} \;

echo "Backup complete: $BACKUP_DIR_DATE"
ls -lh "$BACKUP_DIR_DATE"
```

**Make executable:**

```bash
chmod +x ~/.hermes/scripts/backup_kyber_state.sh
```

**Schedule via cron:**

```bash
# Daily at 3 AM
0 3 * * * ~/.hermes/scripts/backup_kyber_state.sh >> ~/.hermes/logs/backup.log 2>&1
```

Or via Hermes systemd timer (if configured):

```bash
systemctl --user enable --now hermes-backup.timer
```

---

## Manual Backup

For one-off backups before major changes:

```bash
# Snapshot current queue + secrets
SNAPSHOT=~/.hermes/backups/pre-maintenance-$(date +%Y%m%d-%H%M)
mkdir -p "$SNAPSHOT"
cp ~/.hermes/issue_resolution.db ~/.hermes/kanban.db "$SNAPSHOT/"
cp -r ~/.config/claudecode/ "$SNAPSHOT/secrets/"
cp -r ~/.secrets/ "$SNAPSHOT/secrets-full/"

echo "Snapshot: $SNAPSHOT"
du -sh "$SNAPSHOT"
```

---

## Restore Procedures

### Restore Queue After Corruption

If `issue_resolution.db` is corrupted:

```bash
# 1. Stop Hermes
systemctl --user stop hermes-gateway

# 2. Find most recent backup
BACKUP=$(ls -t ~/.hermes/backups/*/issue_resolution.db 2>/dev/null | head -1)

if [ -z "$BACKUP" ]; then
  echo "ERROR: No backup found. Attempting recovery from corrupt DB..."
  sqlite3 ~/.hermes/issue_resolution.db <<'SQL'
.output ~/.hermes/issue_resolution_recovered.sql
.dump
SQL
  mv ~/.hermes/issue_resolution.db ~/.hermes/issue_resolution.db.corrupt
  sqlite3 ~/.hermes/issue_resolution.db < ~/.hermes/issue_resolution_recovered.sql
else
  echo "Restoring from: $BACKUP"
  cp "$BACKUP" ~/.hermes/issue_resolution.db
fi

# 3. Verify integrity
sqlite3 ~/.hermes/issue_resolution.db "PRAGMA integrity_check;"
# Expected: "ok"

# 4. Restart Hermes
systemctl --user start hermes-gateway
```

### Restore Secrets After Loss

If secrets files are missing or corrupted:

```bash
# 1. Find backup
BACKUP=$(ls -t ~/.hermes/backups/*/secrets/kyberm0nk_github_token 2>/dev/null | head -1)

if [ -n "$BACKUP" ]; then
  echo "Restoring GitHub token from: $BACKUP"
  cp "$BACKUP" ~/.secrets/
  
  # Restore launcher configs
  BACKUP_DIR=$(dirname "$BACKUP")
  cp "$BACKUP_DIR"/*.env ~/.config/claudecode/ 2>/dev/null || true
  
  echo "Secrets restored. Verify: gh auth status"
  gh auth status
else
  echo "ERROR: No secrets backup found."
  echo "Manual steps:"
  echo "  1. Regenerate GitHub token at https://github.com/settings/tokens"
  echo "  2. Save to ~/.secrets/kyberm0nk_github_token"
  echo "  3. Update ~/.config/claudecode/claude-local.env with new token path"
fi
```

### Restore Kanban State

```bash
BACKUP=$(ls -t ~/.hermes/backups/*/kanban.db 2>/dev/null | head -1)
if [ -n "$BACKUP" ]; then
  cp "$BACKUP" ~/.hermes/kanban.db
  echo "Kanban restored from: $BACKUP"
else
  echo "WARNING: No kanban backup found. Run kanban sync to rebuild:"
  ~/.hermes/scripts/github_issue_kanban_sync.py
fi
```

---

## Disaster Recovery

Full system rebuild from scratch:

### Step 1: Reinstall Dependencies

```bash
# Guardian (if not already installed)
cd ~/llama_cpp_guardian
./install.sh  # or equivalent setup script

# Hermes Gateway
cd ~/hermes-agent
./install.sh  # or equivalent

# Hermes scripts
# Already in ~/.hermes/scripts/ — no install needed

# Claude Code (if not installed)
# Follow installation guide
```

### Step 2: Restore Backups

```bash
# Find most recent backup
LATEST_BACKUP=$(ls -dt ~/.hermes/backups/*/ | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "ERROR: No backups found. Manual recovery required."
  exit 1
fi

echo "Restoring from: $LATEST_BACKUP"

# Restore databases
cp "$LATEST_BACKUP"/issue_resolution.db ~/.hermes/ 2>/dev/null || true
cp "$LATEST_BACKUP"/kanban.db ~/.hermes/ 2>/dev/null || true

# Restore secrets
cp -r "$LATEST_BACKUP"/secrets/* ~/.config/ 2>/dev/null || true
cp -r "$LATEST_BACKUP"/secrets-full/* ~/.secrets/ 2>/dev/null || true

# Restore Guardian config (if present)
cp "$LATEST_BACKUP"/guardian/config.yaml ~/llama_cpp_guardian/ 2>/dev/null || true
```

### Step 3: Verify and Restart

```bash
# Verify Guardian
curl -sf http://127.0.0.1:11434/healthz && echo "Guardian: OK"

# Verify GitHub
gh auth status

# Start Hermes
systemctl --user start hermes-gateway

# Check queue
sqlite3 ~/.hermes/issue_resolution.db "SELECT COUNT(*) FROM issue_runs WHERE status IN ('running', 'queued');"
```

---

## Backup Verification

Monthly check that backups are working:

```bash
# 1. List recent backups
ls -lt ~/.hermes/backups/ | head -10

# 2. Verify most recent backup has all expected files
LATEST=$(ls -dt ~/.hermes/backups/*/ | head -1)
echo "Checking: $LATEST"
test -f "$LATEST/issue_resolution.db" && echo "✓ issue_resolution.db"
test -f "$LATEST/kanban.db" && echo "✓ kanban.db"
test -f "$LATEST/secrets/kyberm0nk_github_token" && echo "✓ GitHub token"

# 3. Test restore to temporary location
RESTORE_TEST=~/.hermes/restore-test-$(date +%s)
mkdir -p "$RESTORE_TEST"
cp "$LATEST/issue_resolution.db" "$RESTORE_TEST/"
sqlite3 "$RESTORE_TEST/issue_resolution.db" "PRAGMA integrity_check;"
rm -rf "$RESTORE_TEST"
```

---

## Off-Site Backup (Optional)

For disaster recovery beyond local disk:

```bash
# Sync backups to remote host (e.g., backup server)
rsync -avz ~/.hermes/backups/ user@backup-host:~/kyber-backups/

# Or to cloud storage (if configured)
# aws s3 sync ~/.hermes/backups/ s3://your-bucket/kyber-backups/
```

**Note:** Secrets in backups are sensitive. Encrypt before off-site sync:

```bash
tar czf - ~/.hermes/backups/$DATE/ | gpg --encrypt --recipient your-key-id > ~/backup-$DATE.tar.gz.gpg
```

---

## See Also

- [OPERATOR_GUIDE.md](OPERATOR_GUIDE.md) — Production runtime procedures
- [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) — Handling failures and corruption
- [TESTING.md](TESTING.md) — Validation scripts to verify system health after restore
