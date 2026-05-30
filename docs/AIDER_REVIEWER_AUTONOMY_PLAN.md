# Aider Reviewer Autonomy Plan

## Goal

Make the Hermes Aider reviewer loop reliably produce actionable Tier1 findings on active PRs (starting with cryptotrader PR #309), while keeping review and coding responsibilities separated.

## Scope

- Do not fix PR #309 code in this run.
- Fix the Aider reviewer loop behavior only.
- Ensure profile-level reviewer intent is explicit (task + system goal per profile).

## Current Symptoms

1. Tier1 often reports `review_clean` with `Aider output did not contain parseable JSON findings`.
2. Once an `aider-reviewer` comment exists, the loop can skip further review due to coarse `has_real_reviews()` gating.
3. Prompt and parser are too brittle for real Aider terminal output.
4. Tier1/Tier2 role intent is implicit instead of explicitly profile-driven.

## Root-Cause Hypotheses

1. **Skip gate bug**: existing reviewer comments are treated as terminal state and block re-review.
2. **Parser fragility**: extraction only accepts strict JSON blocks; many valid LLM answers include prose wrappers.
3. **Prompt mismatch**: asking for `ONLY JSON` through Aider CLI may conflict with wrapper output.
4. **Profile ambiguity**: no strong per-tier system goals (correctness vs challenge review) causes generic outputs.

## Execution Plan

1. Add explicit reviewer profiles:
   - `tier1`: bug hunter focused on correctness/regressions with concrete evidence.
   - `tier2`: adversarial challenger focused on hidden assumptions and boundary conditions.
2. Add per-profile prompt templates (system goal + output contract).
3. Harden output parsing:
   - Prefer fenced JSON extraction.
   - Add tolerant `{...}` object extraction fallback.
   - Accept a fallback findings format and normalize it.
4. Fix rerun logic:
   - Add `AIDER_REVIEW_TARGET_PR` to force review for one PR even when prior comments exist.
   - Add `AIDER_REVIEW_IGNORE_EXISTING_REVIEWS=true` override for controlled testing.
5. Add tier test harness mode:
   - `AIDER_REVIEW_DRY_RUN=true` to avoid posting comments while validating output quality.
6. Live validation on PR #309 with configured model(s):
   - Run Tier1 repeatedly until we get a normal, parseable review response.
   - Require at least one finding matching already-known issue class (warmup/train boundary overlap in walk-forward split).
7. Document operating profile strategy in this plan + script comments.

## Success Criteria

1. Tier1 returns parseable structured findings (not parse-fail summary).
2. At least one finding references known high-signal issue from PR #309.
3. The loop can be forced to rerun on an already-commented PR for autonomy testing.
4. Tier profiles are explicit and maintainable for future cost-optimized reviewer stacks.

## Non-Goals

- No direct code fix in PR #309.
- No branch merge automation changes.
- No migration away from Aider.

## Rollback

- Keep changes isolated to reviewer loop script.
- If behavior regresses, disable overrides and revert to previous script snapshot.
