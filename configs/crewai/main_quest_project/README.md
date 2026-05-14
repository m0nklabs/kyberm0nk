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
