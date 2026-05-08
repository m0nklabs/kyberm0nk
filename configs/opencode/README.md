# OpenCode Config

OpenCode should act as the Strategist layer.

Planned configuration:

- use Guardian `/v1` as OpenAI-compatible endpoint
- use `DEFAULT_MODEL` for deep planning
- mount active project read-write
- mount reference projects read-only
- avoid direct access to Guardian backend port `11440`

## Model Budget

`scripts/opencode.sh` applies the balanced local coding profile by default:

- `OPENCODE_CONTEXT_WINDOW=65536`
- `OPENCODE_MAX_TOKENS=4096`
- `OPENCODE_TEMPERATURE=0.2`
- `OPENCODE_MAX_OUTPUT_CHARS=20000`

Override these values in `.env` only when intentionally running a larger benchmarked profile.
