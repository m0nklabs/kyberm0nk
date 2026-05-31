#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

./scripts/validate_docs.sh
python3 scripts/validate_kyber_tag_schema.py

echo "quickstart smoke: OK"
