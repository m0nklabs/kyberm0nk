#!/usr/bin/env python3
"""Validate the Kyber PR routing tag schema and bundled examples."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path("docs/kyber-tag.jsonschema")
REQUIRED_FIELDS = {
    "next_action",
    "state",
    "source",
    "tier",
    "model",
    "suggestions_count",
    "content_fingerprint",
}
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{16}$")


def fail(message: str) -> int:
    print(f"kyber-tag schema validation failed: {message}")
    return 1


def enum_values(schema: dict, field: str) -> set[str]:
    values = schema.get("properties", {}).get(field, {}).get("enum", [])
    return {value for value in values if isinstance(value, str)}


def validate_example(schema: dict, example: object, index: int) -> str | None:
    if not isinstance(example, dict):
        return f"example {index} is not an object"

    missing = REQUIRED_FIELDS.difference(example)
    if missing:
        return f"example {index} missing required fields: {sorted(missing)}"

    fingerprint = example.get("content_fingerprint")
    if not isinstance(fingerprint, str) or not FINGERPRINT_RE.fullmatch(fingerprint):
        return f"example {index} has invalid content_fingerprint: {fingerprint!r}"

    for field in ("next_action", "state", "tier"):
        values = enum_values(schema, field)
        value = example.get(field)
        if values and value not in values:
            return f"example {index} has invalid {field}: {value!r}"

    for field in ("source", "model"):
        value = example.get(field)
        if not isinstance(value, str) or not value.strip():
            return f"example {index} has empty {field}"

    suggestions_count = example.get("suggestions_count")
    if not isinstance(suggestions_count, int) or suggestions_count < 0:
        return f"example {index} has invalid suggestions_count: {suggestions_count!r}"

    return None


def main() -> int:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fail(f"missing {SCHEMA_PATH}")
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON in {SCHEMA_PATH}: {exc}")

    required = set(schema.get("required", []))
    if not REQUIRED_FIELDS.issubset(required):
        return fail(f"required fields missing: {sorted(REQUIRED_FIELDS.difference(required))}")

    fingerprint_schema = schema.get("properties", {}).get("content_fingerprint", {})
    if fingerprint_schema.get("pattern") != "^[0-9a-f]{16}$":
        return fail("content_fingerprint must require exactly 16 lowercase hex characters")

    allowed_pairs = {
        ("review_findings", "coding_subagent"),
        ("review_clean", "ready_for_merge"),
        ("ready_for_merge", "ready_for_merge"),
        ("review_inconclusive", "rerun_reviewer"),
        ("review_inconclusive", "tier2_review"),
        ("review_inconclusive", "tier3_review"),
        ("review_findings", "tier1_review"),
        ("review_clean", "tier2_review"),
        ("ready_for_merge", "tier2_review"),
    }
    examples = schema.get("examples", [])
    if not examples:
        return fail("schema must include at least one example")
    for index, example in enumerate(examples, start=1):
        error = validate_example(schema, example, index)
        if error:
            return fail(error)
        # Fail closed: state/next_action pairs must match the routing matrix,
        # not just be individually valid enum values.
        pair = (example.get("state"), example.get("next_action"))
        if pair not in allowed_pairs:
            return fail(f"example {index} has undocumented state/next_action pair: {pair}")

    print("kyber-tag schema validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
