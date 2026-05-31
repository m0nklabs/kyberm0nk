#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

repo = Path('.').resolve()
required = [
    Path('README.md'),
    Path('CONTRIBUTING.md'),
    Path('docs/index.md'),
    Path('docs/ARCHITECTURE.md'),
    Path('docs/GITHUB_ISSUE_RESOLUTION.md'),
    Path('docs/kyber-tag.jsonschema'),
    Path('docs/audit-inventory.csv'),
    Path('docs/audit-inventory.json'),
    Path('docs/audit-report.md'),
]
for path in required:
    if not path.exists():
        print(f'missing required docs artifact: {path}')
        sys.exit(1)

schema = json.loads(Path('docs/kyber-tag.jsonschema').read_text(encoding='utf-8'))
if 'required' not in schema or 'next_action' not in schema['required']:
    print('invalid kyber-tag schema: required fields missing')
    sys.exit(1)
fingerprint_schema = schema.get('properties', {}).get('content_fingerprint', {})
if fingerprint_schema.get('pattern') != '^[0-9a-f]{16}$':
    print('invalid kyber-tag schema: content_fingerprint pattern missing')
    sys.exit(1)
for example in schema.get('examples', []):
    fingerprint = example.get('content_fingerprint') if isinstance(example, dict) else None
    if not isinstance(fingerprint, str) or not re.fullmatch(r'[0-9a-f]{16}', fingerprint):
        print(f'invalid kyber-tag schema example fingerprint: {fingerprint!r}')
        sys.exit(1)

md_paths = [
    Path('README.md'),
    Path('CONTRIBUTING.md'),
    Path('SMOKE_TEST.md'),
    Path('scripts/README.md'),
]
md_paths += sorted(Path('docs').rglob('*.md'))
md_paths += sorted(Path('configs').rglob('README.md'))

link_re = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
broken: list[str] = []
lint_issues: list[str] = []

for path in md_paths:
    text = path.read_text(encoding='utf-8')
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.rstrip() != line:
            lint_issues.append(f'{path}:{lineno}: trailing whitespace')
        if '\t' in line:
            lint_issues.append(f'{path}:{lineno}: tab character')
    for target in link_re.findall(text):
        if target.startswith('http://') or target.startswith('https://') or target.startswith('mailto:'):
            continue
        if target.startswith('#'):
            continue
        clean = target.split('#', 1)[0]
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        try:
            resolved.relative_to(repo)
        except ValueError:
            broken.append(f'{path}: external repo-relative link escaped workspace: {target}')
            continue
        if not resolved.exists():
            broken.append(f'{path}: missing local link target {target}')

if lint_issues:
    print('markdown lint issues:')
    for issue in lint_issues:
        print(issue)
    sys.exit(1)

if broken:
    print('broken markdown links:')
    for issue in broken:
        print(issue)
    sys.exit(1)

# Keep the persisted issue-run state machine consistent across the core docs.
state_docs = [
    Path('docs/GITHUB_ISSUE_RESOLUTION.md'),
    Path('docs/ARCHITECTURE.md'),
    Path('docs/ISSUE_TO_MERGE_TARGET_STATE.md'),
]
for doc in state_docs:
    if not doc.exists():
        continue
    text = doc.read_text(encoding='utf-8')
    for state in ['queued', 'running', 'expanded', 'completed', 'failed']:
        if f'`{state}`' not in text:
            print(f'{doc}: missing persisted issue-run state `{state}`')
            sys.exit(1)

print('docs validation: OK')
PY
