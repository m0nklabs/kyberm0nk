# Contributing

KyberM0nk accepts focused, evidence-based changes.

## Scope

- Keep the active architecture narrative aligned with Hermes, Aider, Guardian, the SQLite-backed issue queue, tiered PR review, and machine-readable `kyber-tag` routing.
- Treat Docker as optional infrastructure, not as the default runtime story.
- Do not introduce GitHub Copilot mentions into PR or issue automation lanes.

## Branches

For docs sync work, use:

```text
docs/sync-<area>-YYYYMMDD
```

Examples:

- `docs/sync-runtime-docs-20260530`
- `docs/sync-audit-report-20260530`

## Commits

Preferred format:

```text
docs: <short subject> (#<issue>)
```

If no issue exists yet, keep the commit message focused and create a follow-up issue later rather than inventing one.

## PR Policy

PR title format:

```text
docs: sync documentation — <area>
```

Every docs PR should include:

1. A short summary.
2. The changed files.
3. Validation steps run.
4. A reference to `docs/audit-report.md`.
5. A machine-readable `kyber-tag` block.

Example:

````text
```kyber-tag
{"next_action":"ready_for_merge","state":"review_clean","checks":{"docs_build":true,"links":true,"linter":true},"artifact_refs":[],"reviewer":"doc-agent","confidence":0.95}
```
````

## Validation

Run this before pushing docs changes:

```bash
scripts/validate_docs.sh
```

Expected result:

```text
docs validation: OK
```

## Archiving Rules

- Never delete documentation directly when it still has historical value.
- Move obsolete or research-heavy material into `archive/research/YYYY-MM-DD/`.
- Add a changelog entry when archiving or moving documentation.
- Keep a short summary and the archive reason at the top of archived Markdown files.

## Safety

- Do not commit secrets.
- Do not rewrite history in log-like documentation.
- Keep examples concrete and reproducible.
