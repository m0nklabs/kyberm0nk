# Aider Config

Aider should act as the Scalpel layer.

Active configuration:

- use Guardian `/v1` as the OpenAI-compatible endpoint
- operate on one active project at a time
- keep patches focused and testable
- prefer the local coder lane for implementation and OpenRouter for review
- participate in the tiered PR review contract through Tier1 and Tier2 reviewer models

The current production review lane is:

- Tier1 reviewer: fast OpenRouter route for first-pass findings
- Tier2 reviewer: stronger OpenRouter route for clean-pass confirmation
- PR-manager routing: machine-readable `kyber-tag` blocks only
