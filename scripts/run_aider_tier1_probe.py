#!/usr/bin/env python3
"""Run a deterministic Tier1 aider review probe against cryptotrader PR 309."""

from __future__ import annotations

import importlib.util
import json
import subprocess

MODULE_PATH = "/home/flip/.hermes/scripts/cryptotrader_pr_aider_reviewer_loop.py"
REPO = "m0nklabs/cryptotrader"
PR_NUMBER = 309


def main() -> int:
    spec = importlib.util.spec_from_file_location("aider_loop", MODULE_PATH)
    if spec is None or spec.loader is None:
        print("ERROR unable to load aider loop module")
        return 1

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    title = subprocess.check_output(
        ["gh", "pr", "view", str(PR_NUMBER), "--repo", REPO, "--json", "title", "--jq", ".title"],
        text=True,
    ).strip()
    diff = subprocess.check_output(["gh", "pr", "diff", str(PR_NUMBER), "--repo", REPO], text=True)
    files_payload = json.loads(
        subprocess.check_output(["gh", "pr", "view", str(PR_NUMBER), "--repo", REPO, "--json", "files"], text=True)
    )
    files = [f.get("path", "") for f in files_payload.get("files", []) if isinstance(f, dict)]

    result = mod.ask_aider_for_review(
        PR_NUMBER,
        title,
        diff,
        ["python: pytest -q tests/test_api_health.py PASS"],
        model=mod.TIER1_MODEL,
        files=files,
    )

    findings = result.get("findings") or []

    print("MODEL_REQUESTED", mod.TIER1_MODEL)
    print("MODEL_FALLBACK", mod.FALLBACK_MODEL)
    print("PARSE_OK", result.get("parse_ok"))
    print("SUMMARY", (result.get("summary") or "")[:600])
    print("FINDINGS_COUNT", len(findings))

    for idx, finding in enumerate(findings[:10], 1):
        if not isinstance(finding, dict):
            continue
        payload = {
            "path": finding.get("path"),
            "line": finding.get("line"),
            "issue": finding.get("issue"),
            "suggestion": finding.get("suggestion"),
        }
        print("FINDING", idx, json.dumps(payload, ensure_ascii=False))

    if not result.get("parse_ok"):
        print("RAW_EXCERPT", (result.get("raw_excerpt") or "")[:3000])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
