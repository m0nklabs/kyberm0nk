# KyberM0nk Claude Instructions

Use the MARK1 operating model as the default instruction layer for Claude Code sessions launched through KyberM0nk.

## Default Global Layer
@../github-copilot-config/.github/agents/MARK1.md

## Local Model Routing Rules
- Claude Code's own runtime model is separate from any application-level model config found in sibling repositories.
- The `claude-local` launcher defaults Claude Code to the Guardian alias `qwen3-35b-uncensored` unless the operator explicitly passes `--model` or sets `CLAUDE_MODEL`.
- Treat project configs such as NerveSplat's `llm.model: gemma4-e4b` as application runtime only. They do not describe or override Claude Code's own runtime model.
- Do not rewrite a sibling app's model setting just to match Claude Code. A project may intentionally use a lighter or different model for its own runtime behavior.
- If asked what model Claude Code is currently using, prefer the active launcher arguments or the current per-session JSONL under `~/.claude/projects/` over historical counters in `~/.claude.json`.

## NerveSplat Note
- NerveSplat can stay on a lighter conversational model such as `gemma4-e4b` for its in-app dialogue loop while Claude Code keeps a stronger coding model for repo work.