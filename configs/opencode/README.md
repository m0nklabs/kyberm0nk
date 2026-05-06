# OpenCode Config

OpenCode should act as the Strategist layer.

Planned configuration:

- use Guardian `/v1` as OpenAI-compatible endpoint
- use `DEFAULT_MODEL` for deep planning
- mount active project read-write
- mount reference projects read-only
- avoid direct access to Guardian backend port `11440`
