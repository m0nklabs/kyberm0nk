#!/usr/bin/env python3
"""Run a deterministic Tier1 aider review probe against cryptotrader PR 309."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path

MODULE_PATH = "/home/flip/.hermes/scripts/cryptotrader_pr_aider_reviewer_loop.py"
REPO = "m0nklabs/cryptotrader"
PR_NUMBER = 309


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Tier1 Aider review probe against a GitHub PR."
    )
    parser.add_argument("--repo", default=REPO, help="GitHub repository in owner/name form.")
    parser.add_argument("--pr", type=int, default=PR_NUMBER, help="Pull request number to review.")
    parser.add_argument(
        "--validation-result",
        action="append",
        default=[],
        help="Real validation evidence to include, e.g. 'pytest -q tests/foo.py PASS'. Repeatable.",
    )
    parser.add_argument(
        "--validation-results-file",
        type=Path,
        help="File containing one validation-result line per command.",
    )
    parser.add_argument(
        "--no-evidence",
        action="store_true",
        help="Permit a probe with no validation evidence; output is diagnostic only.",
    )
    return parser.parse_args()


def load_validation_results(args: argparse.Namespace) -> list[str]:
    results = list(args.validation_result)
    if args.validation_results_file:
        results.extend(
            line.strip()
            for line in args.validation_results_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if results:
        return results
    if args.no_evidence:
        return ["NO_VALIDATION_EVIDENCE: probe output is diagnostic only"]
    raise SystemExit(
        "ERROR no validation evidence supplied. Pass --validation-result, "
        "--validation-results-file, or --no-evidence for an explicitly diagnostic probe."
    )


def main() -> int:
    args = parse_args()
    validation_results = load_validation_results(args)

    spec = importlib.util.spec_from_file_location("aider_loop", MODULE_PATH)
    if spec is None or spec.loader is None:
        print("ERROR unable to load aider loop module")
        return 1

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    title = subprocess.check_output(
        ["gh", "pr", "view", str(args.pr), "--repo", args.repo, "--json", "title", "--jq", ".title"],
        text=True,
    ).strip()
    diff = subprocess.check_output(["gh", "pr", "diff", str(args.pr), "--repo", args.repo], text=True)
    files_payload = json.loads(
        subprocess.check_output(["gh", "pr", "view", str(args.pr), "--repo", args.repo, "--json", "files"], text=True)
    )
    files = [f.get("path", "") for f in files_payload.get("files", []) if isinstance(f, dict)]

    result = mod.ask_aider_for_review(
        args.pr,
        title,
        diff,
        validation_results,
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
