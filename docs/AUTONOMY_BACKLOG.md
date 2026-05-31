# Autonomy Backlog

This backlog consolidates KyberM0nk TODOs, active pipeline notes, and relevant GitHub issue pressure into a ranked execution plan for continuous development mode.

Scoring formula:

```text
priority = impact + urgency + autonomy_multiplier + inverse_complexity
```

- Impact: 1 low, 5 high project value.
- Urgency: 1 can wait, 5 blocks current pipeline confidence.
- Autonomy multiplier: 1 peripheral, 5 directly improves issue -> PR -> review -> merge autonomy.
- Inverse complexity: 5 quick/easy, 1 large/high-complexity.

## Ranked backlog

| Rank | Title | Problem | Impact | Effort | Risk | Dependencies | Owner | Acceptance criteria | I | U | A | C | Score | Wave |
|---:|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | Managed repo branch/drift guard | CryptoTrader can accumulate direct `master`/`main` implementation drift, bypassing branch -> PR review. | Prevents the most damaging pipeline violation. | Small | Low | Local git checkout | Kyber | `scripts/managed_repo_guard.py` fails on protected-branch implementation drift and passes on clean CryptoTrader. | 5 | 5 | 5 | 5 | 20 | 1 |
| 2 | Backlog consolidation and wave plan | TODOs are broad, duplicated, and hard to execute autonomously. | Converts backlog into ranked delivery queue. | Small | Low | Current docs and issues | Kyber | Ranked backlog exists with title, problem, impact, effort, risk, dependencies, owner, acceptance criteria, scores, and waves. | 4 | 5 | 4 | 5 | 18 | 1 |
| 3 | Hermes pre-claim git guard | Hermes can start implementation from a dirty or protected CryptoTrader checkout. | Blocks bad starts before Aider spends tokens or creates drift. | Medium | Medium | Managed repo guard semantics; Hermes execution lane | Hermes | Implemented in Hermes commit `8310636ab`: CryptoTrader Kanban dispatch leaves dirty protected checkout tasks `ready`, records `managed_dispatch_guarded`, and does not claim/spawn. | 5 | 5 | 5 | 3 | 18 | 1 |
| 4 | Branch and PR body contract | PRs can lack issue link, validation evidence, risk notes, or review handoff state. | Makes every autonomous PR reviewable and auditable. | Medium | Low | Hermes issue execution lane | Hermes | Implemented in Hermes commit `d2a052a7c`: CryptoTrader issue branches include the repo slug and PR bodies include linked issue/run, branch/base, validation placeholder, risk notes, and review handoff state. | 5 | 4 | 5 | 3 | 17 | 1 |
| 5 | PR-manager review-findings consumer | `review_findings` can remain advisory text instead of concrete fix work. | Closes the review -> fix loop. | Medium | Medium | Valid `kyber-tag`; PR manager state | Hermes | Implemented in Hermes commit `02b09cbc5`: reviewer output with `kyber-tag.state=review_findings` and `next_action=coding_subagent` requeues the same issue run for same-branch coder fixes instead of marking the run complete. | 5 | 4 | 5 | 3 | 17 | 2 |
| 6 | Pre-merge unresolved findings blocker | A PR could merge while latest current-head tag still has findings. | Protects quality gate integrity. | Medium | Medium | Review tag parser; PR manager | Hermes | Implemented in Hermes commit `7fc85409a`: merge eligibility fails closed unless reviewer output says `ready_for_merge` and its `head_ref_oid` matches the current PR head. | 5 | 4 | 5 | 3 | 17 | 2 |
| 7 | Runtime fail-closed kyber-tag parser | Malformed reviewer output may be treated as clean or retried wastefully. | Prevents unsafe merge signals and review spend loops. | Medium | Medium | Schema and review ingestion path | Hermes | Implemented in Hermes commit `badab438f`: reviewer output must include a valid state/action/current-head tag, malformed output is rerun once, then the issue run fails closed. | 5 | 4 | 4 | 3 | 16 | 2 |
| 8 | OpenRouter preflight command | Operators lack a compact auth/model/rate-limit sanity check before review runs. | Reduces failed review launches and protects connectivity. | Small | Low | OpenRouter key env/file | Kyber | Command checks auth, model availability, and reports available rate-limit headers without full review. | 4 | 4 | 3 | 4 | 15 | 1 |
| 9 | Queue watchdog cron/MoniFuse integration | Queue health exists as a script but is not yet surfaced continuously. | Improves stuck-run detection and operator load. | Small | Low | `scripts/hermes_queue_watchdog.py`; MoniFuse or Hermes cron | Kyber/Hermes | Implemented as tracked `hermes-queue-watchdog.timer` systemd user units plus `--emit on-change` alert/recovery output. | 4 | 4 | 4 | 3 | 15 | 2 |
| 10 | Review-loop circuit breaker | Repeated `review_findings` -> `coding_subagent` can ping-pong indefinitely. | Controls cost and failure loops. | Medium | Medium | Review state history | Hermes | Implemented in Hermes commit `b77f4eef8`: repeated reviewer findings increment a run counter and trip a failed safety gate after the bounded same-branch fix budget. | 4 | 4 | 4 | 3 | 15 | 2 |
| 11 | Automatic merge and issue closure | `ready_for_merge` still needs a complete merge/close/done path. | Completes zero-manual issue-to-merge loop. | Large | High | Pre-merge blocker; CI status checks; permissions | Hermes | Passing clean PR merges, issue closes, Kanban task done, audit comments written. | 5 | 3 | 5 | 1 | 14 | 3 |
| 12 | Audit comments at lifecycle points | Claim, PR, review, fix, merge, and closure transitions are not uniformly auditable. | Improves observability and forensic debugging. | Medium | Low | Hermes state transitions | Hermes | Implemented for GitHub issue/PR transitions in Hermes fork commit `863aad702`: claim, PR open/reuse, review request, review findings routed to same-branch coding, review-loop circuit breaker, and review completion now post compact audit comments. Kanban task audit remains part of automatic merge/closure hardening. | 4 | 3 | 4 | 3 | 14 | 2 |
| 13 | Duplicate suppression for Master Epic issue creation | Crash window can create duplicate sub-issues before SQLite persistence. | Prevents backlog duplication and noisy execution. | Medium | Medium | GitHub search/issue references; SQLite transaction design | Hermes | Implemented in Hermes fork commit `23d979e61`: before creating each Master Epic sub-issue, Hermes searches all issue states for matching `Part of Master Issue #N`, task position, title, and body markers, then records/reuses the existing issue instead of duplicating it. | 4 | 3 | 4 | 3 | 14 | 2 |
| 14 | Per-repo allowlists and cancellation controls | Issue automation needs clearer repo boundaries and operator stop controls. | Reduces accidental cross-repo or unwanted execution. | Medium | Medium | Gateway config; issue lane | Hermes | Only allowlisted repos execute; operator can cancel queued/running work with audit trail. | 4 | 3 | 4 | 3 | 14 | 2 |
| 15 | Priority/capability metadata in `issue_runs` | Lane selection will be weak once more than default Aider exists. | Enables future routing quality. | Medium | Low | Multiple implementation lanes | Hermes | `issue_runs` records priority/capability metadata and routing reason. | 3 | 2 | 4 | 3 | 12 | 3 |
| 16 | Expand reviewer output into anchored inline comments | Review findings may be hard to apply when only summary comments exist. | Improves review quality and fix precision. | Medium | Medium | Diff position mapping; GitHub review API | Hermes/Kyber | Multiple findings post as anchored inline comments where possible, with fallback summary. | 4 | 2 | 3 | 2 | 11 | 3 |
| 17 | Cloud escalation gates | Cloud review/escalation should trigger only on repeated failures or risky diffs. | Controls cost while preserving quality. | Medium | Low | Review state and diff-risk classifier | Kyber | Escalation policy documents and enforces repeated-failure/risky-diff/pre-commit criteria. | 3 | 2 | 3 | 3 | 11 | 3 |
| 18 | Worker MCP registry consultation | Worker wrappers may ask for tools already declared in registry. | Reduces tool confusion. | Medium | Low | MCP registry; worker prompts | Kyber | Worker prompts/wrappers consult `configs/mcp/servers.yaml` before tool requests. | 3 | 2 | 3 | 3 | 11 | 3 |
| 19 | Guardian/AZ cancellation regression tests | Agent Zero/Guardian cancellations may leave orphaned backend requests. | Improves runtime reliability outside core CryptoTrader pipeline. | Medium | Medium | Agent Zero and Guardian test harness | Kyber | Regression catches orphaned `llama-server` requests after cancellation. | 3 | 2 | 2 | 2 | 9 | 3 |
| 20 | Optional direct Claude provider pilot | Direct provider overrides may improve cost/latency but risk auth/routing confusion. | Potential optimization, not current blocker. | Medium | Medium | Disposable workflow slice; local-only settings | Manual/Kyber | Comparison report covers cost, latency, tool reliability, rollback; no global auth changes. | 2 | 1 | 2 | 2 | 7 | 3 |

## Quick wins vs foundational work

Quick wins:

- Managed repo branch/drift guard.
- Backlog consolidation and wave plan.
- OpenRouter preflight command.
- Queue watchdog schedule/visibility integration.

Foundational architecture work:

- Hermes pre-claim git guard.
- Branch and PR body contract.
- PR-manager review-findings consumer.
- Pre-merge blocker.
- Automatic merge and issue closure.

## Execution waves

### Wave 1 — now

Goal: stop known pipeline violations and make the backlog executable.

1. Managed repo branch/drift guard.
2. Backlog consolidation and wave plan.
3. Hermes pre-claim git guard implemented for the direct CryptoTrader issue lane and Kanban dispatcher. (Kanban guard shipped in Hermes commit `8310636ab`.)
4. Branch and PR body contract. (Implemented in Hermes commit `d2a052a7c`.)
5. Compact OpenRouter preflight command. (Implemented as `scripts/openrouter_preflight.py`.)

Success metrics:

- CryptoTrader protected-branch drift is detected before direct issue-lane implementation starts.
- The top autonomy backlog is ranked and deduplicated.
- Future implementation work has concrete acceptance criteria.
- Review/provider preflight can be run before spending full review budget.

### Wave 2 — next

Goal: close the review/fix loop and surface operational health continuously.

1. PR-manager review-findings consumer. (Implemented in Hermes commit `02b09cbc5`.)
2. Pre-merge unresolved findings blocker. (Implemented in Hermes commit `7fc85409a`.)
3. Runtime fail-closed kyber-tag parser. (Implemented in Hermes commit `badab438f`.)
4. Queue watchdog cron/MoniFuse integration. (Implemented as tracked `hermes-queue-watchdog.timer` units.)
5. Review-loop circuit breaker. (Implemented in Hermes commit `b77f4eef8`.)
6. Audit comments at lifecycle transitions. (GitHub issue/PR audit comments implemented in Hermes fork commit `863aad702`; Kanban task audit remains for merge/closure hardening.)
7. Duplicate suppression and per-repo allowlists/cancellation controls.

Success metrics:

- `review_findings` always leads to fix work or explicit escalation.
- PRs cannot merge with unresolved current-head findings.
- Malformed review tags fail closed after one bounded retry.
- Queue health alerts are visible without manual SQLite checks.

### Wave 3 — later

Goal: scale the autonomous pipeline beyond the current single Aider lane.

1. Automatic merge and issue closure.
2. Priority/capability metadata in `issue_runs`.
3. Anchored inline reviewer comments.
4. Cloud escalation gates.
5. Worker MCP registry consultation.
6. Guardian/AZ cancellation regression tests.
7. Optional direct Claude provider pilot.

Success metrics:

- Routine clean PRs merge and close issues automatically.
- Lane selection has recorded capability/priority rationale.
- Review comments are actionable at diff-line granularity.
- Costly cloud/model escalation is bounded and explainable.
