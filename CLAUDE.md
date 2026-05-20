# KyberM0nk Claude Instructions

Use the MARK1 operating model as the default instruction layer for Claude Code sessions launched through KyberM0nk.

## Default Global Layer
@../github-copilot-config/.github/agents/MARK1.md

## Local Model Routing Rules
- Claude Code's own runtime model is separate from any application-level model config found in sibling repositories.
- The `claude-local` launcher defaults Claude Code to the Guardian alias `qwen3-35b-uncensored` unless the operator explicitly passes `--model` or sets `CLAUDE_MODEL`.
- The same launcher should tune Claude-side compaction with environment variables, not by lowering Guardian runtime context. `CLAUDE_CODE_AUTO_COMPACT_WINDOW` and `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` are the right levers for the local 131k Qwen route, with the default Kyber target set to `compact@120k`.
- Treat project configs such as NerveSplat's `llm.model: gemma4-e4b` as application runtime only. They do not describe or override Claude Code's own runtime model.
- Do not rewrite a sibling app's model setting just to match Claude Code. A project may intentionally use a lighter or different model for its own runtime behavior.
- If asked what model Claude Code is currently using, prefer the active launcher arguments or the current per-session JSONL under `~/.claude/projects/` over historical counters in `~/.claude.json`.
- If Claude is about to start a CrewAI run that will use local Guardian workers, Claude must let the current local Guardian/GPU work finish first. Do not kick off Guardian-backed CrewAI workers while Guardian is still busy with local coding requests.
- If a CrewAI run will use OpenRouter providers, Claude must say that cloud credits will be spent. If the control script reports low or critical remaining credits, Claude should tell the operator to top up before leaning on cloud escalation.
- For Kyber CrewAI cloud roles, prefer the MoniFuse top20 value-ranked OpenRouter models. Do not default to premium-priced models outside that pool when a top20 value model already covers the job.
- Claude may assemble or reconfigure a Kyber CrewAI team through the CrewAI MCP instead of staying locked to the seeded role defaults. The seeded per-role models are fallbacks only; Claude may choose any model inside the MoniFuse top20 value pool when it is a better fit for the task.
- If Claude chooses `openai/gpt-5.4` for a Kyber CrewAI OpenRouter role, it should request it with OpenRouter's unified `reasoning` object and set `reasoning.effort` to `xhigh` unless the operator explicitly wants a cheaper or faster pass.

## Context Discipline
- For large files or logs, narrow the target with search first and then use explicit `Read` slices of roughly 200 lines.
- Avoid `@file` whole-file inlines for large files; they burn context quickly and can force avoidable compaction.

## Compact Instructions
- Preserve the exact user goal, active constraints, modified files, validation state, pending commands, and unresolved blockers.
- Keep live operational facts that still affect the next move: active ports, service names, MCP server names, run IDs, worktree or branch names, and operator steering.
- Do not collapse the current local hypothesis or pending validation target into generic prose.
- If context pressure came from a large file or log, preserve the findings and switch to targeted search plus sliced reads instead of dropping recent task state.

## NerveSplat Note
- NerveSplat can stay on a lighter conversational model such as `gemma4-e4b` for its in-app dialogue loop while Claude Code keeps a stronger coding model for repo work.