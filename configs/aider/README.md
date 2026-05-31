# Aider Config

Aider should act as the Scalpel layer.

Active configuration:

- use Guardian `/v1` as the OpenAI-compatible endpoint
- operate on one active project at a time
- keep patches focused and testable
- prefer the local coder lane for implementation and OpenRouter for review
- participate in the tiered PR review contract through Tier1 and Tier2 reviewer models
- use the daily advisor lane only for hard, high-uncertainty problems that need a stronger OpenRouter consultation

The current production review lane is:

- Tier1 reviewer: fast OpenRouter route for first-pass findings
- Tier2 reviewer: stronger OpenRouter route for clean-pass confirmation
- PR-manager routing: machine-readable `kyber-tag` blocks only

Efficiency and resilience rules:

- Keep Tier1 on the fast route; escalate to Tier2 only after a clean Tier1 pass or when the PR manager explicitly needs stronger confirmation.
- Keep duplicate reposting disabled so retries and parallel loops do not spend tokens on the same SHA/tier/fingerprint.
- Keep review fan-out bounded; prefer one active OpenRouter review loop per repo unless a human explicitly accepts higher cloud spend.
- Reduce diff size before increasing model strength when token-per-minute pressure is the bottleneck.
- Use jittered, capped retries for rate-limit resilience; do not switch auth, base URL, or model route as a retry side effect.

The advisor lane is separate from the review lane and is used by Aider only; Hermes may invoke the wrapper, but Hermes itself must not switch to GPT-5.5 as its own model.

The advisor lane is:

- Advisor model: OpenRouter `openrouter/openai/gpt-5.5`
- Availability: once per day across the host
- Intended use: narrow hard questions, architecture ambiguity, or escalation after local attempts stall

## Environment Variables

### Advisor Lane

The daily OpenRouter advisor lane is controlled by:

- `AIDER_ADVISOR_MODEL`: model to use. Default: `openrouter/openai/gpt-5.5`.
- `AIDER_ADVISOR_STATE_DIR`: directory for persisted advisor usage state. Default: `~/.local/state/kyberm0nk`.
- `AIDER_ADVISOR_STATE_FILE`: optional full state file path override. Default: `$AIDER_ADVISOR_STATE_DIR/aider_advisor.json`.
- `AIDER_ADVISOR_DRY_RUN`: if `true`, print what would run without invoking Aider.
- `AIDER_ADVISOR_FORCE`: if `true`, bypass the daily gate and run even if already used today.

The advisor wrapper is `scripts/aider_advisor.py`. It enforces the host-wide once-per-day gate.

### Review Lane

The autonomous PR reviewer loop is controlled by `AIDER_REVIEW_*` variables documented in `.env.example`. The review script path is `~/.hermes/scripts/cryptotrader_pr_aider_reviewer_loop.py` and is managed by Hermes, not by the advisor wrapper.
