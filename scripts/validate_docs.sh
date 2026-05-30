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
    Path('docs/ARCHITECTURE.md'),
    Path('docs/GITHUB_ISSUE_RESOLUTION.md'),
    Path('docs/kyber-tag.jsonschema'),
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

print('docs validation: OK')
PY
