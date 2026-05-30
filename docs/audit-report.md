---
audit_date: 2026-05-30
repository: m0nklabs/kyberm0nk
branch: docs/sync-runtime-docs-20260530
status: pr_open
validation:
  docs_build: true
  links: true
  linter: true
pr_branch: docs/sync-runtime-docs-20260530
pr_url: https://github.com/m0nklabs/kyberm0nk/pull/1
---

# Documentation Audit Report

## Summary

This audit aligns KyberM0nk documentation with the current production path:
Hermes durable orchestration, Aider local implementation, Guardian model
brokering, SQLite-backed issue queue, tiered PR review, and machine-readable
`kyber-tag` routing.

## Actions

- Updated P1 and P2 docs to describe the current end-to-end workflow.
- Added `docs/kyber-tag.jsonschema` and `CONTRIBUTING.md`.
- Added a reproducible docs validation script.
- Added machine-parseable audit inventory artifacts: `docs/audit-inventory.csv` and `docs/audit-inventory.json`.
- Marked obsolete or research-heavy files for archive under `archive/research/2026-05-30/`.
- Applied root-level docs hygiene cleanup and path corrections for the optional workspace file.

## Machine-Parseable Inventory

- `docs/audit-inventory.csv`
- `docs/audit-inventory.json`

## Inventory

| file_path | summary | status | reason | recommended_action | action_taken | pr_branch | pr_url |
| --- | --- | --- | --- | --- | --- | --- | --- |
| README.md | Root overview of the active Kyber stack and entry points. | current | Needed as the top-level operator guide. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| CONTRIBUTING.md | Contribution contract for docs branches, PRs, and kyber-tag usage. | current | Missing before this audit. | update | created | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| CHANGELOG.md | Historical record of structural and docs changes. | current | Needs explicit audit and archive entries. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| SMOKE_TEST.md | Quick smoke surface for the repo. | outdated | Did not reflect the current docs validation path. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/index.md | Docs landing page for P1 navigation and quickstart entry. | current | Required docs index surface for operators and automation. | update | created | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/audit-inventory.csv | Machine-parseable CSV inventory for audit actions. | current | Required explicit CSV deliverable for automation and review. | update | created | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/audit-inventory.json | Machine-parseable JSON inventory for audit actions. | current | Required explicit JSON deliverable for automation and review. | update | created | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| scripts/README.md | High-level catalog of active helper scripts. | current | Needed to expose the docs validation script and active runtime helpers. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/ARCHITECTURE.md | Current runtime architecture and control loop. | current | Core architecture doc must match Hermes + Aider + SQLite + kyber-tag. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/GITHUB_ISSUE_RESOLUTION.md | Durable issue-to-PR automation lane. | current | Needed review-tier and kyber-tag routing updates. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/TOOL_ROLES.md | Role definitions for active tools. | current | Already aligned after earlier tiered review policy update. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/ROADMAP.md | Current and future implementation phases. | current | Needed current reviewer lane wording. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/WORKSPACE_SETUP.md | Workspace and runtime setup guidance. | current | Matches host-native direction. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/WORKSPACE_POLICY.md | Guardrails for repo and workspace ownership. | current | Still matches current operating model. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/WORKSPACE_INVENTORY.md | Canonical inventory of active repos, runtimes, and metadata roots. | current | Still relevant to host-native Kyber. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/SECURITY.md | Security and secret-handling rules. | current | Still aligned with current stack. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/LOCAL_AGENT_MODEL_SETTINGS.md | Benchmark-backed local model budgets. | current | Still part of the active runtime policy. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/VALIDATION_LOG.md | Historical validation evidence. | current | Historical but still relevant for evidence trail. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/AGENT_HANDOFF_PROMPT.md | Handoff guidance for supporting agents. | current | Still part of the active operator workflow. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/SUPERVISOR_LOOP_PLAN.md | Future-facing supervisor design note. | research | Design note, not current implementation. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/CODING_MONSTER_STACK.md | Conceptual multi-project coding cockpit proposal. | research | Conceptual guidance, not the canonical runtime contract. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/VISION_UI.md | Legacy cockpit UI concept centered on sandbox/UI flow. | outdated | Conflicts with the current headless host-native production path. | archive | archived | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.md | Historical model-price analysis reference. | research | Analysis artifact, not part of the current implementation contract. | archive | archived | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/crewai/LLM_COST_PERFORMANCE_ANALYSIS.html | Interactive companion artifact for model-price analysis. | research | Analysis artifact, not active runtime documentation. | archive | archived | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| docs/kyber-tag.jsonschema | Machine-readable schema for PR-manager review tags. | current | Required contract for automation. | update | created | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| configs/README.md | Index for tracked config families. | outdated | Still framed Agent Zero around Docker/runtime wording. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| configs/aider/README.md | Aider runtime policy. | outdated | Still described planned state instead of active policy. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| configs/opencode/README.md | OpenCode runtime policy. | outdated | Still described planned state instead of active host-native policy. | update | updated | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |
| configs/agent-zero/README.md | Agent Zero runtime contract. | current | Already aligned with host-native runtime. | keep | kept | docs/sync-runtime-docs-20260530 | https://github.com/m0nklabs/kyberm0nk/pull/1 |

## Validation Results

| Check | Status | Notes |
| --- | --- | --- |
| docs_build | passed | `scripts/validate_docs.sh` |
| links | passed | Local Markdown link validation runs inside `scripts/validate_docs.sh` |
| linter | passed | Equivalent Markdown hygiene checks run inside `scripts/validate_docs.sh` |
| quickstart_smoke | passed | `scripts/test_quickstart.sh` |

## Archive Criteria Applied

Candidate-for-archive rule used in this audit:

- no meaningful references in active README/docs
- incompatible with the current implementation
- marked or shaped as research/experiment material

Files archived when at least 2 of 3 criteria matched.
