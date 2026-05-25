# Blueprint: Hybrid CrewAI Game-Development Crew

This blueprint defines the direct CrewAI manager crew used by KyberM0nk's main quest: visible game-development orchestration with cheap local Guardian workers and narrow OpenRouter escalation.

## Strategy

The crew should spend local GPU time on context gathering, routine coding, and iteration. Cloud models are reserved for management, final review, and blockers where retry cost would exceed model cost.

## Architecture

Process: `hierarchical`.

The manager owns planning, delegation, escalation, and operator-facing summaries. Local Guardian workers do most meter work. OpenRouter reviewers and specialists are used only when their higher task success rate is worth the price.

## Roles

| Role | Provider | Model | Responsibility |
|------|----------|-------|----------------|
| Main Quest Project Manager | OpenRouter | `deepseek/deepseek-v4-pro` | Slice goals, delegate work, track operator guidance, and gate escalation. |
| Planner | OpenRouter | `deepseek/deepseek-v4-flash` | Cheap planning and progress summaries. |
| Local Game Researcher | Guardian | `gemma4-26b-agent` | Inspect project context and compress findings. |
| Local Game Builder | Guardian | `qwen3-35b-reasoning-agent` | Draft routine implementation work and verification steps. |
| QA Playtest Reviewer | OpenRouter | `google/gemini-3.1-pro-preview-customtools` | Review user-visible quality, tests, and regressions. |
| Expert Escalation Engineer | OpenRouter | `moonshotai/kimi-k2.6` | Handle narrow complex blockers after local attempts fail. |

## Escalation Rules

- Try Guardian first for scanning, summarizing, boilerplate, and small implementation steps.
- Escalate after two failed local attempts on the same blocker.
- Escalate immediately for high-risk architecture changes, destructive operations, hard engine/build failures, or cases where repeated local retries would waste more time than a stronger model costs.
- Keep escalation prompts narrow and include exact failed attempts.

## Direct Runtime Setup

Use the tracked Kyber seed instead of manually recreating the crew:

```bash
scripts/crewai_bootstrap.sh
scripts/crewai_main_quest_dry_run.sh
```

The active Kyber path is direct host-native CrewAI. Legacy Studio wrappers remain only for compatibility and do not define the supported runtime anymore.

See [MAIN_QUEST_PROJECT_MANAGER.md](MAIN_QUEST_PROJECT_MANAGER.md) for the operational workflow.
