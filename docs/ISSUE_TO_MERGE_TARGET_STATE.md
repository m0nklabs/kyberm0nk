# Issue-to-Merge Target State

## Overview

This document defines the complete target state for the KyberM0nk issue-to-merge flow. It covers the state machine, routing contracts between loops, failure handling, and operator visibility. The design is validated against the existing implementation in the Hermes Gateway and Aider runtime.

## 1. State Machine

The issue lifecycle is governed by a five-state machine persisted in `~/.hermes/issue_resolution.db`.

```
                    +---------+
                    |  QUEUED |
                    +---------+
                       |
              enqueue_run() / webhook
                       |
                       v
                    +---------+
                    | RUNNING |
                    +---------+
                       |
              claim_next_run()
                       |
          +------------+------------+
          |                         |
          v                         v
+---------+---------+    +---------+---------+
|  EXPANDED  <-----+    |   EXECUTING       |
| (Master Epic)     |    | (Coder work)      |
+-------------------+    +-------------------+
          |                         |
          |                         v
          |                    +---------+
          |                    |REVIEWING|
          |                    +---------+
          |                         |
          |              +----------+----------+
          |              |                     |
          v              v                     v
+---------+---------+ +---------+      +---------+
| COMPLETED  <------+ | MERGED |      |  FAILED  |
+-------------------+ +--------+      +----------+
```

### States

| State | Meaning | Transition In | Transition Out |
|-------|---------|--------------|----------------|
| `queued` | Run persisted, waiting for single-flight worker | Inserted by `enqueue_run()`, restored by `reset_interrupted_runs()` | Claimed by worker |
| `running` | Worker has claimed the run | `claim_next_run()` updates `queued` to `running` | Executes coder work |
| `expanded` | Master Epic decomposed, sub-issues queued | `_execute_master_issue()` creates sub-issues | Children complete |
| `executing` | Local Aider/Guardian coder work in progress | Entered after claim | Coder work finishes |
| `reviewing` | PR created, tiered reviewers active | Entered after coder work | Review completes |
| `completed` | Issue resolved, review clean, PR ready | Review clean or all children done | Merged or archived |
| `failed` | Execution raised an exception | Catch block in worker | Retried or archived |

### State Transitions

1. **queued -> running**: `claim_next_run()` selects oldest `queued` row (`ORDER BY id ASC LIMIT 1`) and updates to `running`.
2. **running -> executing**: Worker begins Aider invocation.
3. **executing -> reviewing**: Aider finishes, PR opened/found, marked `ready_for_review`.
4. **reviewing -> completed**: Tier1/Tier2 review clean, `kyber-tag` routes to `ready_for_merge`.
5. **reviewing -> executing**: Tier1/Tier2 finds issues, `kyber-tag` routes to `coding_subagent`.
6. **reviewing -> reviewing**: Tier2 rerun, `kyber-tag` routes to `rerun_reviewer`.
7. **executing -> failed**: Exception during coder work.
8. **reviewing -> failed**: Reviewer output unusable or timeout.
9. **failed -> queued**: Retry or manual re-queue.

## 2. Routing Contracts

### 2.1 Sync Loop (Webhook -> Queue)

**Responsibility**: Convert incoming GitHub events into queued runs.

**Contract**:
- Input: GitHub `issues` webhook payload or `/issue` CLI command.
- Output: SQLite `issue_runs` row in `queued` state.
- Idempotency: `find_incomplete_run()` reuses existing `queued`/`running`/`expanded` rows for same repo+issue.
- Master Epic detection: `master-plan` label or body starts with `# Master Project Plan`.
- Sub-issue detection: Body contains `Part of Master Issue #N`.

**Error handling**:
- Malformed payload: Logged, row inserted with `error` field set, worker will retry.
- Duplicate detection: Prevents double-insert during crash windows.

### 2.2 Governor Loop (Queue -> Worker)

**Responsibility**: Manage single-flight execution of the local coder lane.

**Contract**:
- Input: `queued` rows in `issue_runs`.
- Output: Rows transitioned to `running`/`executing`.
- Concurrency: Strict single-flight. Only one Aider/Guardian job at a time.
- FIFO ordering: `ORDER BY id ASC LIMIT 1`.
- Guard: `_QUEUE_GUARD` prevents concurrent worker creation.

**Error handling**:
- Gateway restart: `reset_interrupted_runs()` converts all `running` rows to `queued`.
- Worker crash: Same as restart — interrupted rows become `queued`.
- Capacity protection: Guardian idle check before kicking off Aider work.

### 2.3 Execution Loop (Worker -> Aider)

**Responsibility**: Run Aider against the claimed run's worktree.

**Contract**:
- Input: `running` row with repo, issue_number, workdir, branch.
- Output: Code changes in PR branch, PR marked `ready_for_review`.
- Aider invocation:
  - Local coder: `OPENAI_API_BASE=http://127.0.0.1:11434/v1`, `--model openai/qwen3-35b-uncensored`
  - Branch: `issue/<number>-<slug>` (or caller-provided).
  - Mode: Non-interactive (`--yes --no-gitignore`).
- PR creation: Opens new or reuses existing PR for the branch.

**Error handling**:
- Aider failure: Row marked `failed`, error text stored.
- Branch conflict: Reuses existing branch, commits incrementally.
- PR already exists: Finds existing PR, continues from there.

### 2.4 Reviewer Loop (PR -> Merge)

**Responsibility**: Tiered review with `kyber-tag` routing.

**Contract**:
- Input: PR with `ready_for_review` status.
- Output: `kyber-tag` comment routing next action.
- Tier1 (fast): `deepseek-v4-flash`, posts findings or clean.
- Tier2 (strong): `deepseek-v4-pro`, re-checks if Tier1 clean.
- `kyber-tag` routing:
  - `review_findings` + `coding_subagent` -> back to execution.
  - `review_clean` + `ready_for_merge` -> completed.
  - `review_inconclusive` + `rerun_reviewer` -> rerun Tier2.

**Error handling**:
- Unusable reviewer output: Routes to `rerun_reviewer`.
- Tier2 timeout: Routes to `failed`.
- GitHub API errors: Retried once, then marked `failed`.

## 3. Failure Handling

### 3.1 Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Worker crash | `running` row persists after gateway restart | `reset_interrupted_runs()` -> `queued` |
| Aider timeout | Timeout exception in worker loop | Marked `failed`, retried on next cycle |
| Review timeout | Tier1/Tier2 exceeds deadline | Marked `failed`, retried |
| GitHub API error | `gh` command returns non-zero | Retried once, then `failed` |
| Guardian unavailable | Connection refused on `11434/v1` | Marked `failed`, logged |
| Master Epic duplicate | Guardian returns existing issue refs | Reuses existing sub-issues |
| Branch conflict | Git reports conflicts during push | Reuses branch, commits incrementally |

### 3.2 Retry Policy

- Single-flight worker retries `failed` rows after a backoff period.
- Max retries: Configurable (default: 3).
- Retry count stored in `attempt_count` field.
- Next retry time stored in `next_attempt_at`.

### 3.3 Operator Visibility

- **SQLite inspection**: `sqlite3 ~/.hermes/issue_resolution.db 'SELECT * FROM issue_runs ORDER BY id DESC LIMIT 20;'`
- **Master sub-issues**: `sqlite3 ~/.hermes/issue_resolution.db 'SELECT * FROM master_subissues ORDER BY master_run_id, position;'`
- **Gateway logs**: All transitions logged with timestamps.
- **Home channel notifications**: Sent on queue resume, completion, and failure.
- **PR comments**: Review findings posted as inline PR comments with `kyber-tag` blocks.

## 4. Architecture Documentation

### 4.1 Component Diagram

```
+------------------+     +------------------+     +------------------+
|  Sync Loop       |     |  Governor Loop   |     |  Execution Loop  |
|  (Webhook/CLI)   |---->|  (Queue Manager) |---->|  (Aider Worker)  |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +------------------+     +------------------+
|  GitHub API      |     |  SQLite DB       |     |  PR Branch       |
|  (issues webhook)|     |  (issue_runs)    |     |  (issue/N-slug)  |
+------------------+     +------------------+     +------------------+
                                                        |
                                                        v
                                               +------------------+
                                               |  Reviewer Loop   |
                                               |  (Tier1 + Tier2) |
                                               +------------------+
                                                        |
                                                        v
                                               +------------------+
                                               |  kyber-tag       |
                                               |  Routing Table   |
                                               +------------------+
```

### 4.2 Data Flow

1. **Event intake**: Webhook or CLI -> Hermes -> `/issue` command -> `enqueue_run()`.
2. **State persistence**: `IssueStateStore` writes to `~/.hermes/issue_resolution.db`.
3. **Claim**: `_issue_queue_worker()` calls `claim_next_run()` -> selects oldest `queued`.
4. **Execution**: Aider invoked with role envelope -> code changes committed -> PR updated.
5. **Review**: Tier1 -> Tier2 -> `kyber-tag` parsed -> next action routed.
6. **Completion**: `ready_for_merge` -> PR merged -> row marked `completed`.

### 4.3 Configuration Points

| Config | Location | Purpose |
|--------|----------|---------|
| Guardian URL | `OPENAI_API_BASE` | Local model endpoint |
| Aider model | `--model` flag | Model for coder/reviewers |
| Tier1 model | `openrouter/deepseek/deepseek-v4-flash` | Fast reviewer |
| Tier2 model | `openrouter/deepseek/deepseek-v4-pro` | Strong reviewer |
| DB path | `~/.hermes/issue_resolution.db` | State persistence |
| Max retries | Configurable (default 3) | Retry policy |
| Branch prefix | `issue/` | PR branch naming |
| Master plan label | `master-plan` | Master Epic detection |

## 5. Runnable Checklist

### Pre-flight Checks

- [ ] Guardian is healthy on `http://127.0.0.1:11434/v1`.
- [ ] SQLite DB exists at `~/.hermes/issue_resolution.db`.
- [ ] GitHub token is valid (`gh auth status` returns success).
- [ ] Aider is available at `~/aider/.venv/bin/aider`.
- [ ] OpenRouter API key is set (`OPENROUTER_API_KEY`).

### Execution Checks

- [ ] `enqueue_run()` creates a `queued` row.
- [ ] `claim_next_run()` selects oldest `queued` row.
- [ ] Aider invocation completes successfully.
- [ ] PR is created or found for the branch.
- [ ] PR is marked `ready_for_review`.
- [ ] Tier1 reviewer posts findings or clean.
- [ ] Tier2 reviewer (if needed) posts findings or clean.
- [ ] `kyber-tag` comment is posted with valid JSON.
- [ ] Next action is routed correctly.

### Post-completion Checks

- [ ] Row status is `completed` or `failed`.
- [ ] PR exists and contains code changes.
- [ ] `kyber-tag` routing is correct.
- [ ] Master sub-issues are recorded (if applicable).
- [ ] Gateway logs show clean transition.

### Validation

Run the full validation:

```bash
scripts/test_quickstart.sh
```

Expected output:

```
docs validation: OK
quickstart smoke: OK
```

## 6. In-Scope / Out-of-Scope

### In Scope
- GitHub issue ingestion (webhook + CLI).
- Master Epic decomposition and sub-issue creation.
- Single-flight local coder execution (Aider + Guardian).
- Tiered PR review (Tier1 + Tier2 via OpenRouter).
- `kyber-tag` routing for next actions.
- SQLite state persistence and gateway resume.
- Operator visibility (logs, DB, PR comments).

### Out of Scope
- External CI/CD pipeline integrations.
- Modifications outside `/home/flip/kyberm0nk`.
- GitHub Copilot mentions in PR/issue automation.
- Docker-based execution (host-native is default).
- OpenCode, Agent Zero, and CrewAI as primary lanes (evaluation candidates).
