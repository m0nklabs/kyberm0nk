# KyberM0nk Docs Index

This index maps the current KyberM0nk runtime documentation to the active architecture contract.

## P1 Entry Docs

- [README.md](../README.md)
- [Quickstart in README](../README.md#quickstart)
- [Workspace Setup](WORKSPACE_SETUP.md)

## P2 Architecture and State

- [Architecture](ARCHITECTURE.md)
- [Automated GitHub Issue Resolution](GITHUB_ISSUE_RESOLUTION.md)
- [Issue-to-Merge Target State](ISSUE_TO_MERGE_TARGET_STATE.md)
- [Autonomy Backlog](AUTONOMY_BACKLOG.md)
- [Roadmap](ROADMAP.md)

## Operations

Practical reference for running Hermes in production:

- [Operator Guide](OPERATOR_GUIDE.md) — Hermes lifecycle, queue management, common issues, recovery procedures
- [Testing Guide](TESTING.md) — Validation scripts, pass/fail criteria, dependencies for all test runners
- [Incident Response](INCIDENT_RESPONSE.md) — P1-P4 severity classification, runbooks for crashes, corruption, rate limits
- [Backup and Recovery](BACKUP.md) — Auto-backup script, restore procedures, disaster recovery rebuild
- [Configuration Reference](CONFIGURATION.md) — All environment variables for launchers, Hermes, Guardian, CryptoTrader
- [Harbor Evaluations](HARBOR_EVALS.md) — Cross-framework Harbor wrapper and local Claude/Hermes/Aider benchmark defaults

## P3 Contracts

- [Kyber Tag Schema](kyber-tag.jsonschema)
- [Contributing](../CONTRIBUTING.md)
- [Tool Roles](TOOL_ROLES.md)

## P4 Future Options

- [Claude Provider Overrides Idea](CLAUDE_PROVIDER_OVERRIDES_IDEA.md)

## P5 Archive and Historical Material

- [Audit Report](audit-report.md)
- [Archive Root](../archive/research/2026-05-30/)

## Validation

Run:

```bash
scripts/test_quickstart.sh
scripts/validate_docs.sh
scripts/validate_kyber_tag_schema.py
```

Expected result:

```text
docs validation: OK
```
