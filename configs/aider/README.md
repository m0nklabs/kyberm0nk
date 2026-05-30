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

The advisor lane is separate from the review lane and is used by Aider only; Hermes may invoke the wrapper, but Hermes itself must not switch to GPT-5.5 as its own model.

The advisor lane is:

- Advisor model: OpenRouter `openrouter/openai/gpt-5.5`
- Availability: once per day across the host
- Intended use: narrow hard questions, architecture ambiguity, or escalation after local attempts stall
