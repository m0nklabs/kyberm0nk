# Agent Zero Config

Agent Zero should act as the Operator layer.

Planned configuration:

- run via Docker
- mount the active project read-write only when required
- mount reference projects read-only
- do not mount Docker socket by default
- log all task output with timestamps

## Model Budget

Agent Zero uses a loop-safe local coding profile for routine sandbox work:

- Guardian alias: `gemma4-26b-agent`
- chat model: `ctx_length: 65536`, `ctx_history: 0.35`, `max_tokens: 1536`, `timeout: 240s`
- utility model: `ctx_length: 32768`, `ctx_input: 0.35`, `max_tokens: 1024`, `timeout: 180s`

The goal is to provide enough context for real coding tasks while preventing long repetitive thought loops. If Agent Zero starts repeating itself, run `scripts/agent_zero_unstick.sh` to stop the current UI process, reprovision tracked config, and start the UI again.

## Operating Discipline

Agent Zero's project instructions must emphasize effectiveness, not only correctness. A command can be valid and coherent while still failing to move the task forward.

For sandbox workers, prefer instructions that force this cycle:

1. State the expected observable effect of the next action.
2. Run one focused tool action.
3. Compare the result against the previous state.
4. Continue only if the state changed toward the goal.
5. If two actions produce the same state, stop that route and report the blocker or choose a different route.

This keeps local models useful even when they are weaker than cloud coding agents: they can still execute good small steps, but they need explicit pressure to notice non-progress.
