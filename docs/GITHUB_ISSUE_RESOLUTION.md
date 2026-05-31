# Automated GitHub Issue Resolution

Kyber's issue-resolution lane matures a project through GitHub issues and PRs. It is implemented inside the headless Hermes Gateway as `/issue` — a persistent, single-flight automation lane that uses only the active server-side stack: Hermes, Aider, Guardian, GitHub CLI, SQLite, and OpenRouter.

Hermes assigns exactly one queued issue at a time to the coding-agent lane. That coding agent resolves the issue in a PR, marks the PR `ready_for_review`, and only then does the review loop begin.

This is the core mechanism by which Kyber matures any project — cryptotrader is the active testing playground.

The lane is production-ready for controlled daemon use: requests are persisted
before execution, local Aider/Guardian work is processed FIFO, interrupted runs
are restored on gateway startup, and Master Epics can be decomposed into ordered
GitHub sub-issues. It does not require an active editor, GUI, IDE plugin, or
interactive desktop session. It reacts to CLI, Telegram, and webhook events and
then continues autonomously from persisted state.

## Lane Selection and Assignment Contract

Hermes assigns exactly one queued issue at a time to the coding-agent lane through a strict single-flight contract:

1. **Lane selection**: Today, Hermes routes all normal issues and sub-issues to the Aider lane. Master Epics are routed to Guardian for decomposition, then their sub-issues are routed to Aider.
2. **Claim contract**: `claim_next_run()` selects the oldest `queued` row (`ORDER BY id ASC LIMIT 1`), marks it `running`, and executes the coder work. Only one row should be `running` for the local coder lane at a time.
3. **Guard rails**: `_QUEUE_GUARD` prevents concurrent worker creation inside the gateway process. `_QUEUE_WORKER_TASK` tracks the active worker.
4. **Availability**: Hermes does not currently run a lane health probe before assignment. If Aider or Guardian is unavailable after claim, the run is failed or remains `running` until gateway restart resets it to `queued`.
5. **Persistence**: The `running` state is persisted in SQLite before any coder work begins. Gateway restart triggers `reset_interrupted_runs()`, which converts interrupted `running` rows back to `queued`.
6. **Lease semantics**: There is no explicit persisted lease timeout yet. The worker holds the run until completion, failure, or gateway restart.

## Architecture

The lane has five headless execution layers:

1. **Trigger layer**: A Hermes Gateway `/issue` command from a messaging
  platform or a GitHub `issues` webhook creates an `IssueResolutionRequest`.
2. **Classification layer**: Hermes loads the issue via `gh issue view` and
   classifies it as a normal issue, Master Epic, or sub-issue.
3. **Persistence layer**: `IssueStateStore` writes the run to
   `~/.hermes/issue_resolution.db` before any local coder work starts.
4. **Single-flight worker**: `_issue_queue_worker()` claims the oldest queued
   run and processes exactly one local Aider/Guardian job at a time.
5. **Review layer**: successful coder runs open or find a PR, then invoke the
  tiered reviewer lane through OpenRouter. Tier1 is the fast reviewer and
  Tier2 is the stronger reviewer. Reviewer comments emit machine-readable
  `kyber-tag` blocks so the PR manager can route the next action.

The implementation lives in Hermes:

- `gateway/issue_resolution.py`: state machine, queue worker, Aider invocations,
  GitHub issue/PR operations, and Guardian decomposition.
- `gateway/run.py`: `/issue` command dispatch and gateway-startup queue resume.
- `gateway/platforms/webhook.py`: GitHub `issues` webhook conversion into the
  same `/issue` lane.
- `hermes_cli/commands.py`: command registry entry for gateway `/issue`.

## Manual Trigger

```bash
/issue m0nklabs/cryptotrader 10 --workdir /home/flip/cryptotrader
```

The gateway stores the request, starts the worker if needed, and returns a queued
message such as `Hermes: Issue #10 queued as run #42. Local coder execution is
single-flight.` Status updates are delivered through the source platform for
operator visibility, but execution does not depend on that client staying
connected.

Local coder execution is strict single-flight. If another issue is already in
the local Aider/Guardian lane, the new run stays queued in SQLite until the
current run finishes.

## Master Epic Detection

Hermes treats an issue as a Master Epic when either condition is true:

- The issue has the `master-plan` label.
- The issue body starts with `# Master Project Plan` after leading whitespace is
  ignored.

For Master Epics, Hermes asks Guardian to decompose the plan into ordered atomic
tasks, creates one GitHub sub-issue per task, writes `Part of Master Issue #X` in
each sub-issue body, and queues those sub-issues sequentially through the same
`/issue` lane.

Guardian is called through the local OpenAI-compatible endpoint at
`http://127.0.0.1:11434/v1/chat/completions`. The decomposition model resolves
in this order:

1. `HERMES_ISSUE_DECOMPOSE_MODEL`
2. `DEFAULT_MODEL`
3. `qwen3-35b-uncensored`

The parser expects JSON shaped as:

```json
{
  "tasks": [
    {
      "title": "Implement persistent issue queue",
      "body": "Add SQLite-backed run persistence and resume logic."
    }
  ]
}
```

String-only task items are accepted and are used as both title and body. Task
titles are capped at 180 characters before sub-issue creation.

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

The webhook adapter only changes the prompt construction path when a route sets:

```yaml
automation: github_issue_resolution
```

All existing webhook safety rails remain active: route secrets, event filtering,
rate limiting, idempotency cache, and body-size limits are still enforced by the
generic webhook platform.

## SQLite State Machine

State lives in `~/.hermes/issue_resolution.db`. The main table is `issue_runs`;
Master Epic child mapping is stored in `master_subissues`.

### `issue_runs`

| Column | Purpose |
| --- | --- |
| `id` | Monotonic FIFO run id. |
| `repo` | GitHub repository in `owner/name` form. |
| `issue_number` | GitHub issue number being processed. |
| `workdir` | Local checkout path used by Aider. |
| `branch` | Optional caller-provided branch name. |
| `status` | Current run status. |
| `run_type` | `issue`, `master`, or `sub_issue`. |
| `parent_run_id` | Parent Master Epic run id for sub-issues. |
| `master_issue_number` | Source Master Epic issue number for sub-issues. |
| `pr_number` / `pr_url` | PR created or found for completed coder runs. |
| `error` | Truncated failure text for failed runs. |
| `attempt_count` | Number of execution attempts used by retry policy. |
| `next_attempt_at` | Unix timestamp for next retry eligibility. |
| `created_at` / `updated_at` | Unix timestamps used for audit and ordering. |

### Statuses

| Status | Meaning | Mutation path |
| --- | --- | --- |
| `queued` | Run is persisted and waiting for the single-flight worker. | Inserted by `enqueue_run()` or restored by `reset_interrupted_runs()`. |
| `running` | Worker has claimed the oldest queued run. | `claim_next_run()` selects `ORDER BY id ASC LIMIT 1` and updates that row before execution. |
| `expanded` | Master Epic was decomposed and its sub-issues were queued. | `_execute_master_issue()` creates sub-issues, records them, queues child runs, then calls `mark_expanded()`. |
| `completed` | Normal/sub-issue run has opened or found a PR and reviewer feedback has been posted; Master Epic has all children completed. | `_execute_single_issue()` calls `mark_completed()` after review feedback; `_complete_ready_masters()` completes expanded parents after every child is completed. |
| `failed` | Execution raised an exception. | `_issue_queue_worker()` catches the exception, stores truncated error text, notifies the operator, and keeps draining later queued work. |

Duplicate submission protection is status-aware. `find_incomplete_run()` reuses
an existing `queued`, `running`, or `expanded` run for the same repo and issue
instead of inserting a second active row.

### `master_subissues`

`master_subissues` records the generated task position, title, body, and GitHub
sub-issue number. A unique `(master_run_id, position)` constraint prevents the
same decomposed task position from being recorded twice during a retry.

## FIFO and Single-Flight Execution

The local coder path is intentionally conservative because Guardian and Aider
share scarce local inference capacity.

- `submit_issue_resolution()` persists the run and calls
  `ensure_issue_queue_worker()`.
- `_QUEUE_GUARD` prevents concurrent worker creation inside the gateway process.
- `_QUEUE_WORKER_TASK` tracks the active worker.
- `_issue_queue_worker()` repeatedly calls `claim_next_run()`.
- `claim_next_run()` selects only `queued` rows, ordered by `id ASC`, and marks
  the selected row `running` before execution starts.

This means local Aider/Guardian coding is FIFO and single-flight even when
multiple Telegram commands or webhook events arrive close together.

Cloud review happens after the local coder finishes and a PR exists. The review
invocation uses OpenRouter and does not change the local FIFO policy.

## Review Routing

The reviewer lane is intentionally GitHub-Copilot-free.

Issue-to-PR handoff before review is explicit:

1. Hermes triages a new issue and routes it to the local coding-agent lane.
2. The coding agent opens or reuses a PR branch and resolves the issue inside that PR.
3. After local checks pass, the coding agent marks the PR `ready_for_review`.
4. Only then does the PR review loop start (Tier1 -> Tier2 -> `kyber-tag` routing).

- Tier1 reviewer posts findings immediately when it sees a high-signal issue.
- If Tier1 is clean, Tier2 reviewer re-checks with a stronger model.
- Reviewer comments include a `kyber-tag` block that the PR manager parses.

Canonical next-action routing:

| Review result | `kyber-tag.state` | `kyber-tag.next_action` | Gate effect |
| --- | --- | --- | --- |
| Findings posted | `review_findings` | `coding_subagent` | Blocking: PR must not merge until a follow-up commit addresses findings and a later review returns clean, or an operator applies an explicit merge override. |
| No issues after Tier2 | `review_clean` | `ready_for_merge` | Merge-eligible only when repository CI and scoped validation gates are also green. |
| Reviewer output unusable | `review_inconclusive` | `rerun_reviewer` | Blocking until one bounded rerun succeeds; repeated inconclusive output escalates to an operator instead of being treated as clean. |

The PR manager must treat review tags as durable state, not advisory prose. A tag
with `state=review_findings` remains open while the PR head SHA matches the tag's
reviewed SHA. A later code commit may clear only the handoff condition, not the
finding itself; merge readiness still requires a fresh reviewer tag with
`state=review_clean` and `next_action=ready_for_merge` unless an explicit operator
override is recorded.

Additional review-loop safety gates:

- **Substantive-review gate:** at least one parseable Aider reviewer tag is
  required. Smoke tests, failed Copilot reviews, or comments saying a reviewer
  could not run do not count as review coverage.
- **Review-churn gate:** more than five review dismissals in one hour is abnormal
  and must pause auto-merge for operator inspection.
- **Mixed-scope gate:** PRs that combine CI/workflow edits with application logic
  require either split PRs or an explicit `meta:ci+logic` override label.
- **Diff-scoped validation gate:** reviewer evidence should prefer tests and
  static checks related to touched files; unrelated environment failures are
  reported separately so they do not drown out review findings.

## Startup Resume and Crash Recovery

Hermes Gateway calls `resume_issue_resolution_queue()` during startup from
`GatewayRunner.start()`.

The resume flow is deliberately simple:

1. `reset_interrupted_runs()` changes every `running` row back to `queued`.
2. `count_pending_runs()` counts remaining queued work.
3. If pending work exists, Hermes sends a home-channel notice when possible and
   starts the single-flight worker.
4. The worker resumes by claiming the oldest queued row.

This recovers crashes, gateway restarts, and host reboots where a local coder run
was interrupted before marking the row `completed`, `expanded`, or `failed`.

## Aider Roles

Local coder:

```bash
OPENAI_API_BASE=http://127.0.0.1:11434/v1 \
OPENAI_API_KEY=$AIDER_GUARDIAN_API_KEY \
/home/flip/aider/.venv/bin/aider --model openai/qwen3-35b-uncensored --yes --no-gitignore --message "$PROMPT"
```

Tier1 reviewer:

```bash
OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
OPENAI_API_KEY=$OPENROUTER_API_KEY \
/home/flip/aider/.venv/bin/aider --model openrouter/deepseek/deepseek-v4-flash --cache-prompts --no-auto-commits --yes --no-gitignore --message "$PROMPT"
```

See `.env.example` for the complete list of `AIDER_REVIEW_*` environment variables
that control the review loop behaviour (model selection, dedup window, force-rerun
overrides, dry-run mode, size limits).

Tier2 reviewer:

```bash
OPENROUTER_API_KEY=$OPENROUTER_API_KEY \
OPENAI_API_KEY=$OPENROUTER_API_KEY \
/home/flip/aider/.venv/bin/aider --model openrouter/deepseek/deepseek-v4-pro --cache-prompts --no-auto-commits --yes --no-gitignore --message "$PROMPT"
```

## Current Scope

- Runs as a headless Hermes Gateway automation lane.
- Creates/checks out an `issue/<number>-<slug>` branch.
- Detects Master Epics via `master-plan` label or `# Master Project Plan` body.
- Decomposes Master Epics through Guardian.
- Creates sub-issues with `Part of Master Issue #X` references.
- Queues issue runs in SQLite at `~/.hermes/issue_resolution.db`.
- Resets interrupted `running` rows to `queued` on gateway startup.
- Processes local coder work through a strict single-flight FIFO worker.
- Reuses incomplete active rows for the same repo and issue.
- Runs local Aider against Guardian.
- Pushes the branch.
- Opens or finds a GitHub PR.
- Runs tiered cloud Aider reviewers against OpenRouter.
- Emits machine-readable `kyber-tag` review routing comments for the PR manager.
- Posts reviewer feedback as an inline PR comment when a diff anchor is found,
  otherwise as a normal PR comment.

## Queue Health Watchdog

Kyber ships a read-only queue-health watchdog at
`scripts/hermes_queue_watchdog.py`. It inspects `issue_runs` in
`~/.hermes/issue_resolution.db` and emits JSON or text without mutating the
queue. The default thresholds are documented in `.env.example`:

- stale `running` rows after two hours without a fresh update;
- old `queued` rows after one hour of waiting;
- queue-depth pressure above five queued rows;
- recent failure pressure at three failed rows in the last 24 hours;
- WIP-limit violation when more than one row is `running`.

Recommended operator check:

```bash
scripts/hermes_queue_watchdog.py --output text
```

Recommended automation mode:

```bash
scripts/hermes_queue_watchdog.py --fail-on-alert
```

Alerts are self-improvement triggers. Stale `running` rows should lead to an
operator-audited requeue/fail decision, queue-depth pressure should trigger
triage or lane-capability planning, and repeated failures should feed the
supervisor loop before more retries are spent.

## Next Hardening

- Integrate the queue-health watchdog with Hermes cron or MoniFuse so stale
  `running` rows, old `queued` rows, and queue-depth backpressure alert without
  manual SQLite inspection.
- Add priority and capability metadata once Hermes has more than the default Aider
  implementation lane; until then, FIFO remains the safer local-capacity policy.
- Add review-loop circuit breakers so repeated `review_findings` ->
  `coding_subagent` cycles escalate instead of ping-ponging indefinitely.
- Add per-repo allowlists and richer concurrency controls for cloud review.
- Add cancellation and retry controls.
- Add richer reviewer output parsing for multiple inline comments.
- Add duplicate prevention for crash windows between `gh issue create` and state write.
- Teach the Guardian decomposition parser to detect existing issue references
  such as `#182` and link/reuse them instead of blindly creating new sub-issues.

## SQLite Inspection

```bash
sqlite3 ~/.hermes/issue_resolution.db \
  'SELECT id, repo, issue_number, run_type, status, parent_run_id, pr_number FROM issue_runs ORDER BY id;'
```

Useful Master Epic inspection:

```bash
sqlite3 ~/.hermes/issue_resolution.db \
  'SELECT master_run_id, position, sub_issue_number, title FROM master_subissues ORDER BY master_run_id, position;'
```

## See Also

- [ISSUE_TO_MERGE_TARGET_STATE.md](ISSUE_TO_MERGE_TARGET_STATE.md) — complete target state with state machine, routing contracts, failure handling, and runnable checklist.