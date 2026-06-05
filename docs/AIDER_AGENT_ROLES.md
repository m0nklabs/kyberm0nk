# Aider Agent Roles — Iron-Strong Prompts

This document describes the autonomous agent pipeline for CryptoTrader, where Hermes (as PR Manager) orchestrates specialized Aider agents with distinct roles.

## Overview

The pipeline has three primary Aider agent roles:

1. **Aider Researcher (ORC)** — Analyzes GitHub issues, understands codebase, creates implementation plans
2. **Aider Coder** — Executes implementation plans, writes tested code, creates PRs
3. **Aider Reviewer** (Tier1 & Tier2) — Reviews code for bugs, security, and subtle failures

Each role has an "iron-strong" system prompt that defines its responsibilities, decision framework, and output format. These prompts are the single source of truth for agent behavior.

## System Prompts

### Location

All prompts are stored in:
```
~/.hermes/prompts/aider/
├── researcher.md          # Aider Researcher (ORC) system prompt
├── coder.md              # Aider Coder system prompt
├── reviewer_tier1.md     # Tier1 Reviewer system prompt
└── reviewer_tier2.md     # Tier2 Reviewer system prompt (adversarial)
```

### Prompt Loading

Scripts load prompts at runtime:

**Reviewer loop** (`cryptotrader_pr_aider_reviewer_loop.py`):
```python
def _load_prompt_file(name: str) -> str:
    prompt_path = HERMES_HOME / "prompts" / "aider" / f"{name}.md"
    return prompt_path.read_text(encoding="utf-8")

PROFILE_PROMPTS = {
    "tier1": _load_prompt_file("reviewer_tier1"),
    "tier2": _load_prompt_file("reviewer_tier2"),
}
```

**Coder launcher** (`cryptotrader_pr_coder_launcher.py`):
```python
def _load_coder_prompt() -> str:
    prompt_path = HERMES_HOME / "prompts" / "aider" / "coder.md"
    return prompt_path.read_text(encoding="utf-8")
```

**Issue resolution** (`issue_resolution.py`):
```python
def _load_researcher_prompt() -> str:
    prompt_path = Path.home() / ".hermes" / "prompts" / "aider" / "researcher.md"
    return prompt_path.read_text(encoding="utf-8")
```

---

## Role: Aider Researcher (ORC)

**Purpose**: Transform vague GitHub issues into detailed, executable implementation plans.

**Prompt file**: `~/.hermes/prompts/aider/researcher.md`

### What the Researcher Does

1. **Issue decomposition**: Breaks complex issues into discrete components
2. **Codebase investigation**: Maps architecture, data flow, state management
3. **Solution design**: Evaluates 2-3 approaches, selects best with justification
4. **Implementation planning**: Step-by-step plan with file changes, edge cases, test strategy
5. **Risk assessment**: Identifies risks and mitigation strategies
6. **Output formatting**: Structured markdown plan ready for Coder execution

### Output Format

```markdown
## Implementation Plan for Issue #XYZ

### Problem Analysis
- **Core issue**: [One sentence]
- **Root cause**: [Why it exists]
- **Impact**: [Who/what is affected]

### Proposed Solution
**Approach**: [Selected approach]
**Justification**: [Why this approach]
**Alternatives considered**: [List with rejection reasons]

### Implementation Steps
#### Step 1: [Action verb + object]
- **Files to modify**: `path/to/file.py`
- **Changes**: [Detailed description]
- **Rationale**: [Why needed]
- **Edge cases**: [Potential issues]

### Test Strategy
**Unit tests**: ...
**Integration tests**: ...
**Manual validation**: ...

### Risk Assessment
**Risks**: [List with mitigations]
**Out of scope**: [Deferred items]

### Success Criteria
- [ ] [Measurable criteria]

### Branch and PR Strategy
**Branch name**: `hermes/issue-XYZ-description-YYYYMMDD`
**Commit message**: ...
**PR title/body**: ...
```

### Key Principles

- **Specificity**: Every file change has detailed description
- **Test coverage**: Every code change has corresponding test plan
- **Edge cases**: Identify failure modes and how to handle them
- **No ambiguity**: Plan must be executable by Coder without additional analysis

---

## Role: Aider Coder

**Purpose**: Execute implementation plans, write tested code, create PRs.

**Prompt file**: `~/.hermes/prompts/aider/coder.md`

### What the Coder Does

1. **Plan validation**: Reads plan, verifies prerequisites, identifies ambiguities
2. **Implementation**: Executes steps sequentially, writes code, runs tests
3. **Validation**: Full test suite, linters, manual checks
4. **Commit & push**: Atomic commit with Co-Authored-By trailer, push to remote
5. **PR creation**: Uses template from plan, captures PR URL

### Two Modes

**Mode 1: Full Implementation** (from Researcher plan)
- Creates branch, implements all steps, runs tests, pushes, creates PR

**Mode 2: Review Findings Fix** (from Reviewer)
- Checks out PR branch, fixes specific findings, commits, pushes, updates PR

### Output Format

**On success** (full implementation):
```
## Implementation Complete
**Branch**: hermes/issue-XYZ-description-YYYYMMDD
**PR**: #123 (URL: ...)
**Status**: Ready for review
**Tests passing**: 15/15
```

**On success** (review fix):
```
## Review Finding Fixed
**PR**: #123
**Finding addressed**: [description]
**Tests passing**: 15/15
```

### Key Principles

- **Execute exactly**: Follow plan without creative interpretation
- **Test continuously**: Run tests after every significant change
- **Fix failures immediately**: Do not proceed if tests fail
- **Minimal changes**: Do not refactor code not in the plan
- **Proper attribution**: Include Co-Authored-By trailer in commits

---

## Role: Aider Reviewer (Tier1)

**Purpose**: Fast, high-confidence review for obvious bugs and regressions.

**Prompt file**: `~/.hermes/prompts/aider/reviewer_tier1.md`

**Model**: `openrouter/deepseek/deepseek-v4-flash` (fast)

### What Tier1 Reviews

**Focus areas** (in priority order):
1. Correctness: Logic errors, wrong assumptions
2. Security: Data leakage, injection, auth bypass
3. Boundary conditions: Off-by-one, empty/null, overflow
4. State management: Race conditions, stale state
5. Error handling: Unhandled exceptions, missing validation
6. Test adequacy: Missing coverage for risky paths

### What NOT to Report

- Style nits (spacing, naming)
- Refactoring suggestions without bugs
- Dependency metadata churn
- "Could be better" without failure mode
- Advisory observations

### Output Format

```json
{
  "summary": "One paragraph summarizing PR and findings",
  "findings": [
    {
      "path": "api/routes.py",
      "line": 42,
      "issue": "Description of the bug",
      "suggestion": "How to fix it",
      "replacement": "```suggestion\ncode block\n```"
    }
  ]
}
```

**Constraints**:
- 0-5 findings (highest severity only)
- Exact file path + 1-based line number
- Concrete failure mechanism required
- Medium severity or higher only

---

## Role: Aider Reviewer (Tier2)

**Purpose**: Adversarial review that catches subtle failures Tier1 missed.

**Prompt file**: `~/.hermes/prompts/aider/reviewer_tier2.md`

**Model**: `openrouter/deepseek/deepseek-v4-pro` (strong)

### What Tier2 Reviews

**Assumes Tier1 already found obvious bugs.** Focuses on:

1. **Hidden coupling**: Non-obvious dependencies
2. **State leakage**: Shared state across requests/tests
3. **Metric math errors**: Division, sign, denominator issues
4. **Statistical bias**: Implementation biasing results
5. **Train/test contamination**: ML data leakage
6. **Warmup/ordering issues**: Code that works only on second run
7. **Edge case blindness**: Empty, zero, boundary, duplicates
8. **Test coverage gaps**: Tests that pass while bug exists

### Adversarial Techniques

- Challenge every assumption (empty input? malformed? boundary?)
- Trace data flow (where does it come from? what if assumptions wrong?)
- Break invariants (what if check is wrong? what if passes but should fail?)
- Stress test statistics (denominator zero? rounding errors? order of operations?)
- Audit test adequacy (can test pass while bug exists?)

### Special Patterns

- **Silent failure**: Code that fails silently with default value
- **Race condition**: Works sequentially, fails concurrently
- **Accumulator**: State that accumulates without reset
- **Boundary assassin**: Works for typical inputs, fails at boundaries
- **Test mirage**: Tests that pass while bug persists

### Output Format

Same JSON schema as Tier1, but findings must be:
- **Subtle** (Tier1 would have missed them)
- **Verifiable** (exact failure mechanism explained)
- **High impact** (correctness, security, accuracy)

---

## The Review Loop

The two-tier review system ensures both obvious and subtle bugs are caught:

```
┌─────────────────────────────────────────────┐
│  Hermes (PR Manager) creates/takes PR       │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Aider Reviewer Tier1                       │
│  - Fast pass for obvious bugs               │
│  - Model: deepseek-v4-flash                 │
└──────────────────┬──────────────────────────┘
                   │
                   ├─ Findings? ──► Aider Coder fixes ──► Tier1 again
                   │
                   └─ Clean?
                        │
                        ▼
┌─────────────────────────────────────────────┐
│  Aider Reviewer Tier2                       │
│  - Adversarial review                       │
│  - Model: deepseek-v4-pro                   │
└──────────────────┬──────────────────────────┘
                   │
                   ├─ Findings? ──► Aider Coder fixes ──► Tier1 again (back!)
                   │
                   └─ Clean?
                        │
                        ▼
              ┌─────────────────┐
              │  Ready to merge │
              └─────────────────┘
```

**Key flow**:
1. Tier1 reviews for obvious bugs
2. If findings → Coder fixes → Tier1 reviews again
3. If Tier1 clean → Tier2 adversarial review
4. If Tier2 finds issues → Coder fixes → **Back to Tier1** (not just Tier2!)
5. Only when both tiers clean → PR ready for merge

### Closed-PR Recovery (Agent Handoff)

When a PR is **closed without merge** (by operator decision, CI failures, pollution), the review loop is broken — there is no open branch to route findings to. All three agent roles have explicit system-prompt guidance for this:

| Agent | Behavior when PR is closed-without-merge |
|-------|-----------------------------------------|
| **Aider Reviewer Tier1** | Refuse to review. Emit `next_action: researcher-replan` in manager tag. Do NOT route to coder. |
| **Aider Reviewer Tier2** | Refuse adversarial review. Same `researcher-replan` routing. |
| **Aider Coder** | Refuse to code (cannot push to closed branch). Emit `status: refuse`, hand back to PR Manager. |
| **Hermes (PR Manager)** | Before starting new work, run `gh pr list --state all` for the issue. If prior PR closed without merge, read prior attempt's failure mode, create fresh branch from current `master`, link closed PR in new PR body as `Supersedes #NNN`. |
| **Aider Researcher** | Before planning, investigate why the prior attempt was closed. Differentiate the new approach, scope it tighter, branch from fresh master. |

**Handoff sequence** when PR #337 closes without merge:
```
Operator closes PR #337
    ↓
Next reviewer cron tick sees PR closed
    ↓
Reviewer emits next_action: researcher-replan
    ↓
Coder cron sees closed PR → refuses
    ↓
Next issue dispatch picks up the open issue
    ↓
Hermes worker (or Researcher) reads closed PR's history
    ↓
Fresh branch from current master → new PR with "Supersedes #337"
```

**Anti-pattern**: Do NOT route closed-without-merge findings to the Coder. The branch is dead and pushing to it is impossible. Always hand back to research/planning.

---

## Cron Jobs Driving the Pipeline

All automation runs on cron jobs defined in `~/.hermes/cron/jobs.json`:

| Job | Interval | Script | Purpose |
|-----|----------|--------|---------|
| GitHub Inbox Triage | 120m | Agent prompt | Ingest issues → kanban cards |
| PR Governor | 30m | `cryptotrader_pr_governor.py` | Classify PRs as feature/bulk |
| PR Execution Lane | 10m | `cryptotrader_pr_execution_lane.py` | Queue PR actions |
| Aider Reviewer Loop | 30m | `cryptotrader_pr_aider_reviewer_loop.py` | Tier1/Tier2 reviews |
| PR Coder Launcher | 20m | `cryptotrader_pr_coder_launcher.py` | Fix review findings |
| Review Required Bridge | 15m | `cryptotrader_review_required_pr_bridge.py` | Scratch → dir workspace |
| PR Result Sync | 10m | `cryptotrader_pr_result_sync.py` | Sync results to PR meta |

---

## Model Routing

Each agent uses appropriate models based on cost/speed tradeoffs:

| Agent | Model | Reason |
|-------|-------|--------|
| Researcher | `openai/qwen3-35b-uncensored` (Guardian local) | Needs deep codebase understanding |
| Coder | `openrouter/deepseek/deepseek-v4-flash` | Fast, focused code changes |
| Reviewer Tier1 | `openrouter/deepseek/deepseek-v4-flash` | Fast review, high volume |
| Reviewer Tier2 | `openrouter/deepseek/deepseek-v4-pro` | Strong adversarial analysis |

**Cost optimization**: Flash models for fast iteration, Pro models only for adversarial review.

---

## Co-Authored-By Trailers

Every automated commit and PR includes attribution:

**Git commit**:
```
feat: add feature X

Closes #123

Co-Authored-By: Aider Coder (tier1) <openrouter/deepseek/deepseek-v4-flash>
```

**PR body**:
```
Co-Authored-By: Aider Researcher (tier1) <openai/qwen3-35b-uncensored>
```

**PR comment**:
```
**Agent:** Aider Reviewer | **Model:** openrouter/deepseek/deepseek-v4-flash | **Tier:** tier1 | **Task:** automated-review
```

Implemented via `co_author_utils.py`:
```python
co_author_trailer("Aider Coder", "tier1", "openrouter/deepseek/deepseek-v4-flash")
# → "Co-authored-by: Aider Coder (tier1) <openrouter/deepseek/deepseek-v4-flash>"
```

---

## Updating Prompts

The iron-strong prompts are the single source of truth. To update them:

1. Edit the prompt file in `~/.hermes/prompts/aider/`
2. Scripts load prompts at runtime, so changes take effect on next cron run
3. Test with a new issue to verify behavior
4. Commit prompt changes to hermes-agent repo

**Prompt versioning**: Each prompt file should have a version comment at the top:
```markdown
<!-- Version: 2.0 - Iron-strong rewrite, 2026-06-04 -->
```

---

## Debugging Agent Behavior

When an agent behaves unexpectedly:

1. **Check logs**: `~/.hermes/cron/logs/<script_name>.log`
2. **Check state**: `~/.hermes/cron/<script_name>_state.json`
3. **Run script manually**:
   ```bash
   cd ~/.hermes
   python3 scripts/cryptotrader_pr_aider_reviewer_loop.py --dry-run
   ```
4. **Check prompt**: Verify the prompt file exists and has correct content
5. **Check model**: Verify model is responding (test with simple prompt)

---

## Related Documentation

- `docs/ARCHITECTURE.md` — Overall Hermes + Aider architecture
- `docs/ISSUE_TO_MERGE_TARGET_STATE.md` — Five-state issue resolution machine
- `docs/GITHUB_ISSUE_RESOLUTION.md` — Headless execution layers
- `docs/AGENT_HANDOFF_PROMPT.md` — Agent handoff protocol
- `docs/WORKSPACE_POLICY.md` — Scratch vs dir workspace semantics
- `~/hermes-agent/skills/devops/kanban-worker/SKILL.md` — Kanban worker pitfalls

---

## Version History

- **2026-06-04** (v2.0): Iron-strong rewrite of all prompts
  - Researcher: Added structured output format, decision framework, examples
  - Coder: Added two modes (plan execution vs review fix), error handling
  - Reviewer Tier1: Focused on correctness, concrete failure modes
  - Reviewer Tier2: Adversarial techniques, special patterns, deep analysis

- **2026-05** (v1.0): Initial minimal prompts
  - Researcher: 8-line prompt ("create branch, write code, push")
  - Coder: Inline prompt in coder launcher
  - Reviewer: Inline prompts in reviewer loop

---

## Summary

The autonomous pipeline relies on **iron-strong system prompts** that clearly define each agent's role, decision framework, and output format. These prompts are:

- **Specific**: No ambiguity about responsibilities
- **Structured**: Standard output formats for machine parsing
- **Complete**: Cover edge cases, error handling, quality standards
- **Versioned**: Tracked in files for easy updates

The three-tier agent system (Researcher → Coder → Reviewer) with two-tier review (Tier1 fast + Tier2 adversarial) provides robust automation with human-quality gates.

For questions or contributions, see the prompt files in `~/.hermes/prompts/aider/`.
