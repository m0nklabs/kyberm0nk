# Main Quest CrewAI Project

This directory is the direct CrewAI version of the Studio main quest crew. It is
anchored to the NewNexus Unreal Engine project by default.

Files:

- `crew.yaml`: crew process, manager, planning LLM, and provider policy.
- `agents.yaml`: agent roles and role-specific model choices.
- `tasks.yaml`: ordered task graph and context dependencies.
- `tools.yaml`: GitHub repository search tool scoped to `m0nklabs/NewNexus`.
- `crew.py`: Python runner that builds the CrewAI objects from YAML and can run a dry build check.

Runtime safety knobs in `crew.py`:

- `--repo-write-mode disabled|enabled`: controls whether `newnexus_github_push` may actually write to GitHub during the run.
- `--github-target-branch <name>`: sets the default GitHub branch for push attempts when writes are enabled.

Runtime kickoff guardrails in `scripts/crewai_main_quest_control.py`:

- Live runs that use Guardian workers wait for Guardian `/api/status` to go idle before kickoff, so the same local GPU route is not contended by an already-active local coding session.
- Live runs that use OpenRouter providers emit a cloud-spend warning before kickoff and attempt a `/credits` balance check when the configured OpenRouter key is a management key.
- The control-script status payload persists the last kickoff policy summary under `guardian_local_policy`, `openrouter_credit_policy`, and `llm_usage` so Claude/MCP tooling can explain why a run waited or why cloud spend needs attention.

OpenRouter default model policy for this project:

- Keep routine cloud orchestration inside the MoniFuse top20 value list instead of defaulting to premium-priced OpenRouter models outside that pool.
- Current defaults are fallback seeds, not hard pins: `deepseek/deepseek-v4-flash` for the manager, `z-ai/glm-4.7-flash` for planning, `z-ai/glm-5.1` for QA review, and `deepseek/deepseek-v4-pro` for narrow escalations.
- Claude may use the CrewAI MCP to assemble or reconfigure a team and pick a different OpenRouter model when it is a better fit for the task, as long as that model stays inside the MoniFuse top20 value pool documented in `configs/crewai/model_policy.yaml`.
- When that selected model is `openai/gpt-5.4`, the expected OpenRouter request profile is `extra_body.reasoning.effort=xhigh` with reasoning blocks excluded unless the run explicitly needs them returned.

The GitHub search tool is path-aware for file-style queries. Exact queries such as `NewNexus.uproject` or `Source/NewNexus/NewNexus.Build.cs` attempt a direct repository file fetch before falling back to GitHub code search, which keeps live Unreal context gathering anchored to real files instead of docs mentions.

Dry-run inside the CrewAI-Studio container:

```bash
scripts/crewai_main_quest_dry_run.sh
```

The dry-run builds the CrewAI objects without calling any model.

The GitHub tool uses the GitHub REST API and reads its token from `GITHUB_TOKEN` or `GH_TOKEN`; keep the token in the ignored Studio `.env`, not in Git.

For first live pilots, prefer `--repo-write-mode disabled` until the crew has shown that its searches, planning, and validation commands are grounded in the actual NewNexus files.

Default target context:

- GitHub repository: `m0nklabs/NewNexus`
- Host checkout: `.agent-projects/NewNexus`
- Agent Zero workspace: `/a0/usr/projects/newnexus`
- Engine target: Unreal Engine 5.7
