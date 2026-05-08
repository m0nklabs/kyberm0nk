# Agent Zero Config

Agent Zero should act as the Operator layer.

Planned configuration:

- run via Docker
- mount the active project read-write only when required
- mount reference projects read-only
- do not mount Docker socket by default
- log all task output with timestamps

## Model Budget

Agent Zero uses the balanced local coding profile from `docs/LOCAL_AGENT_MODEL_SETTINGS.md`:

- chat model: `ctx_length: 65536`, `ctx_history: 0.55`, `timeout: 420s`
- utility model: `ctx_length: 32768`, `ctx_input: 0.45`, `timeout: 240s`

The goal is to provide enough context for real coding tasks without defaulting to the slowest possible Guardian request shape. Keep long, high-output jobs explicit and benchmarked.
