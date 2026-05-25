# Agent Zero Config

Agent Zero should act as the Operator layer.

Active configuration:

- run host-native from `~/agentzero`
- keep runtime home under `~/agentzero/runtime/home`
- keep runtime secrets under `~/agentzero/runtime/secrets`
- restore tracked projects into `~/agentzero/usr/projects`
- keep the real NewNexus source checkout at `~/NewNexus` and restore only project metadata under `~/agentzero/usr/projects/newnexus/.a0proj`
- log all task output with timestamps

Bootstrap and launch with:

```bash
scripts/agent_zero_bootstrap.sh
scripts/agent_zero_up.sh
```

The current launcher serves the UI on `http://127.0.0.1:50001` and clears stale listeners on that port before restart, including root-owned leftovers from the retired Docker sandbox when `sudo -n` is available.

## Model Budget

Agent Zero uses a loop-safe local coding profile for routine host-runtime work:

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
