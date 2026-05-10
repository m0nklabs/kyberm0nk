# Main Quest CrewAI Project

This directory is the direct CrewAI version of the Studio main quest crew.

Files:

- `crew.yaml`: crew process, manager, planning LLM, and provider policy.
- `agents.yaml`: agent roles and role-specific model choices.
- `tasks.yaml`: ordered task graph and context dependencies.
- `crew.py`: Python runner that builds the CrewAI objects from YAML and can run a dry build check.

Dry-run inside the CrewAI-Studio container:

```bash
scripts/crewai_main_quest_dry_run.sh
```

The dry-run builds the CrewAI objects without calling any model.
