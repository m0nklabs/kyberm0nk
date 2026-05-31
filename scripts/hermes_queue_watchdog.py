#!/usr/bin/env python3
"""Inspect Hermes issue-run queue health and emit improvement signals.

The watchdog is intentionally read-only. It reports stale running rows, old queued
rows, queue-depth pressure, and recent failed-run pressure from the Hermes
`issue_runs` SQLite table.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path("~/.hermes/issue_resolution.db")
DEFAULT_LOG_PATH = REPO_ROOT / "logs" / "hermes_queue_watchdog" / "hermes_queue_watchdog.jsonl"
DEFAULT_RUNNING_STALE_SECONDS = 2 * 60 * 60
DEFAULT_QUEUED_STALE_SECONDS = 60 * 60
DEFAULT_QUEUE_DEPTH_THRESHOLD = 5
DEFAULT_FAILED_RECENT_SECONDS = 24 * 60 * 60
DEFAULT_FAILED_THRESHOLD = 3


def env_int(name: str, default: int) -> int:
    """Read a positive integer from the environment."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ.get("HERMES_ISSUE_DB", str(DEFAULT_DB_PATH))),
        help="Hermes issue-resolution SQLite DB path.",
    )
    parser.add_argument(
        "--running-stale-seconds",
        type=int,
        default=env_int("HERMES_QUEUE_STALE_RUNNING_SECONDS", DEFAULT_RUNNING_STALE_SECONDS),
        help="Alert when a running row has not updated within this many seconds.",
    )
    parser.add_argument(
        "--queued-stale-seconds",
        type=int,
        default=env_int("HERMES_QUEUE_STALE_QUEUED_SECONDS", DEFAULT_QUEUED_STALE_SECONDS),
        help="Alert when a queued row has waited this many seconds.",
    )
    parser.add_argument(
        "--queue-depth-threshold",
        type=int,
        default=env_int("HERMES_QUEUE_DEPTH_THRESHOLD", DEFAULT_QUEUE_DEPTH_THRESHOLD),
        help="Alert when queued rows exceed this count.",
    )
    parser.add_argument(
        "--failed-recent-seconds",
        type=int,
        default=env_int("HERMES_QUEUE_FAILED_RECENT_SECONDS", DEFAULT_FAILED_RECENT_SECONDS),
        help="Lookback window for recent failed rows.",
    )
    parser.add_argument(
        "--failed-threshold",
        type=int,
        default=env_int("HERMES_QUEUE_FAILED_THRESHOLD", DEFAULT_FAILED_THRESHOLD),
        help="Alert when recent failed rows reach this count.",
    )
    parser.add_argument("--now", type=int, help="Unix timestamp override for deterministic checks.")
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="Optional JSONL log path.")
    parser.add_argument("--no-log", action="store_true", help="Do not append the JSONL watchdog log.")
    parser.add_argument("--fail-on-alert", action="store_true", help="Exit non-zero when alerts are present.")
    parser.add_argument("--output", choices=("text", "json"), default="json", help="Output format.")
    return parser.parse_args()


def unix_now(args: argparse.Namespace) -> int:
    """Return the current Unix timestamp."""
    if args.now is not None:
        return args.now
    return int(datetime.now(timezone.utc).timestamp())


def open_readonly_db(path: Path) -> sqlite3.Connection:
    """Open SQLite database in read-only mode."""
    resolved = path.expanduser().resolve()
    uri = f"file:{resolved}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return column names for a table."""
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def fetch_all(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Fetch rows as dictionaries."""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def age_expr(columns: set[str]) -> str:
    """Return the best available timestamp expression for row age."""
    if "updated_at" in columns:
        return "COALESCE(updated_at, created_at, 0)"
    if "created_at" in columns:
        return "COALESCE(created_at, 0)"
    return "0"


def select_fields(columns: set[str]) -> str:
    """Return a safe field list for issue_runs inspection."""
    candidates = [
        "id",
        "repo",
        "issue_number",
        "run_type",
        "status",
        "parent_run_id",
        "master_issue_number",
        "pr_number",
        "attempt_count",
        "next_attempt_at",
        "created_at",
        "updated_at",
        "error",
    ]
    fields = [name for name in candidates if name in columns]
    return ", ".join(fields) if fields else "rowid AS id"


def inspect_queue(conn: sqlite3.Connection, now: int, args: argparse.Namespace) -> dict[str, Any]:
    """Inspect queue state and return alerts plus KPI facts."""
    columns = table_columns(conn, "issue_runs")
    if not columns:
        raise RuntimeError("missing issue_runs table")

    fields = select_fields(columns)
    timestamp = age_expr(columns)
    counts = fetch_all(conn, "SELECT status, COUNT(*) AS count FROM issue_runs GROUP BY status ORDER BY status")
    counts_by_status = {str(row["status"]): int(row["count"]) for row in counts}

    stale_running = fetch_all(
        conn,
        f"""
        SELECT {fields}, (? - {timestamp}) AS age_seconds
        FROM issue_runs
        WHERE status = 'running' AND (? - {timestamp}) >= ?
        ORDER BY age_seconds DESC, id ASC
        LIMIT 25
        """,
        (now, now, args.running_stale_seconds),
    )
    old_queued = fetch_all(
        conn,
        f"""
        SELECT {fields}, (? - {timestamp}) AS age_seconds
        FROM issue_runs
        WHERE status = 'queued' AND (? - {timestamp}) >= ?
        ORDER BY age_seconds DESC, id ASC
        LIMIT 25
        """,
        (now, now, args.queued_stale_seconds),
    )
    recent_failed = fetch_all(
        conn,
        f"""
        SELECT {fields}, (? - {timestamp}) AS age_seconds
        FROM issue_runs
        WHERE status = 'failed' AND {timestamp} >= ?
        ORDER BY {timestamp} DESC, id DESC
        LIMIT 25
        """,
        (now, now - args.failed_recent_seconds),
    )

    queued_count = counts_by_status.get("queued", 0)
    running_count = counts_by_status.get("running", 0)
    failed_recent_count = len(recent_failed)

    alerts: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []

    if stale_running:
        alerts.append(
            {
                "type": "stale_running",
                "severity": "P0",
                "count": len(stale_running),
                "threshold_seconds": args.running_stale_seconds,
                "message": "One or more Hermes runs are stuck in running without a fresh update.",
            }
        )
        recommendations.append(
            {
                "action": "escalate_or_requeue",
                "confidence": 0.92,
                "reason": "Running rows beyond the lease threshold consume the single-flight lane and block throughput.",
                "operator_prompt": "Inspect the stale run, verify no active worker owns it, then requeue or fail it with an audit note.",
            }
        )

    if queued_count > args.queue_depth_threshold:
        alerts.append(
            {
                "type": "queue_depth",
                "severity": "P1",
                "count": queued_count,
                "threshold_count": args.queue_depth_threshold,
                "message": "Hermes queued work exceeds the configured WIP/backlog threshold.",
            }
        )
        recommendations.append(
            {
                "action": "triage_backlog",
                "confidence": 0.86,
                "reason": "Single-flight FIFO plus growing queue depth predicts rising lead time.",
                "operator_prompt": "Split urgent P0/P1 items, defer low-value queued work, or add a separate lane only after capability metadata exists.",
            }
        )

    if old_queued:
        alerts.append(
            {
                "type": "old_queued",
                "severity": "P1",
                "count": len(old_queued),
                "threshold_seconds": args.queued_stale_seconds,
                "message": "One or more queued runs have waited longer than the freshness target.",
            }
        )
        recommendations.append(
            {
                "action": "review_fifo_health",
                "confidence": 0.82,
                "reason": "Old queued rows indicate idle-worker, hidden-blocker, or queue-depth pressure.",
                "operator_prompt": "Check Guardian/Aider availability and confirm the queue worker is alive before adding more work.",
            }
        )

    if failed_recent_count >= args.failed_threshold:
        alerts.append(
            {
                "type": "recent_failures",
                "severity": "P1",
                "count": failed_recent_count,
                "threshold_count": args.failed_threshold,
                "window_seconds": args.failed_recent_seconds,
                "message": "Recent failed runs crossed the failure-pressure threshold.",
            }
        )
        recommendations.append(
            {
                "action": "run_supervisor_review",
                "confidence": 0.88,
                "reason": "Repeated failures are a self-improvement signal, not just per-issue noise.",
                "operator_prompt": "Cluster failure errors, add a durable guardrail or prompt/wrapper fix, then retry only the affected lane.",
            }
        )

    if running_count > 1:
        alerts.append(
            {
                "type": "wip_limit_violation",
                "severity": "P0",
                "count": running_count,
                "threshold_count": 1,
                "message": "More than one running issue violates the local Aider/Guardian single-flight WIP limit.",
            }
        )
        recommendations.append(
            {
                "action": "pause_new_claims",
                "confidence": 0.95,
                "reason": "Concurrent local coder work can contend for Guardian capacity and corrupt assignment ownership.",
                "operator_prompt": "Pause queue claims and reconcile which run, if any, has a live worker before continuing.",
            }
        )

    total_terminal = counts_by_status.get("completed", 0) + counts_by_status.get("failed", 0)
    defect_escape_rate = counts_by_status.get("failed", 0) / total_terminal if total_terminal else 0.0
    blocked_task_ratio = (len(stale_running) + len(old_queued)) / max(1, queued_count + running_count)

    return {
        "timestamp": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        "db": str(args.db.expanduser()),
        "thresholds": {
            "running_stale_seconds": args.running_stale_seconds,
            "queued_stale_seconds": args.queued_stale_seconds,
            "queue_depth_threshold": args.queue_depth_threshold,
            "failed_recent_seconds": args.failed_recent_seconds,
            "failed_threshold": args.failed_threshold,
        },
        "counts": counts_by_status,
        "kpis": {
            "blocked_task_ratio": round(blocked_task_ratio, 4),
            "stale_task_count": len(stale_running) + len(old_queued),
            "queue_depth": queued_count,
            "active_wip": running_count,
            "recent_failed_count": failed_recent_count,
            "defect_escape_rate_proxy": round(defect_escape_rate, 4),
        },
        "alerts": alerts,
        "stale_running": stale_running,
        "old_queued": old_queued,
        "recent_failed": recent_failed,
        "recommendations": recommendations,
        "status": "alert" if alerts else "ok",
    }


def missing_db_record(args: argparse.Namespace, now: int) -> dict[str, Any]:
    """Return a non-failing record when Hermes has not created the DB yet."""
    return {
        "timestamp": datetime.fromtimestamp(now, timezone.utc).isoformat(),
        "db": str(args.db.expanduser()),
        "status": "unavailable",
        "counts": {},
        "kpis": {
            "blocked_task_ratio": 0.0,
            "stale_task_count": 0,
            "queue_depth": 0,
            "active_wip": 0,
            "recent_failed_count": 0,
            "defect_escape_rate_proxy": 0.0,
        },
        "alerts": [],
        "recommendations": [
            {
                "action": "verify_hermes_gateway",
                "confidence": 0.7,
                "reason": "The issue-resolution database is absent, so queue health cannot be measured yet.",
                "operator_prompt": "Start Hermes Gateway or confirm this host is not expected to run the /issue lane.",
            }
        ],
    }


def append_log(path: Path, payload: dict[str, Any]) -> None:
    """Append a JSONL watchdog record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def render_text(record: dict[str, Any]) -> str:
    """Render concise text output for operators."""
    lines = [
        "Hermes queue watchdog",
        f"- Status: {record['status']}",
        f"- DB: {record['db']}",
        f"- Counts: {json.dumps(record.get('counts', {}), sort_keys=True)}",
        f"- KPIs: {json.dumps(record.get('kpis', {}), sort_keys=True)}",
    ]
    alerts = record.get("alerts", [])
    if alerts:
        lines.append("- Alerts:")
        for alert in alerts:
            lines.append(f"  - {alert['severity']} {alert['type']}: {alert['message']}")
    recommendations = record.get("recommendations", [])
    if recommendations:
        lines.append("- Recommendations:")
        for recommendation in recommendations[:5]:
            lines.append(f"  - {recommendation['action']}: {recommendation['operator_prompt']}")
    return "\n".join(lines)


def main() -> int:
    """Run one read-only queue-health inspection."""
    args = parse_args()
    now = unix_now(args)
    db_path = args.db.expanduser()

    if not db_path.exists():
        record = missing_db_record(args, now)
    else:
        try:
            with open_readonly_db(args.db) as conn:
                record = inspect_queue(conn, now, args)
        except sqlite3.OperationalError as exc:
            record = {
                "timestamp": datetime.fromtimestamp(now, timezone.utc).isoformat(),
                "db": str(args.db.expanduser()),
                "status": "error",
                "error": str(exc),
                "counts": {},
                "kpis": {},
                "alerts": [
                    {
                        "type": "watchdog_error",
                        "severity": "P1",
                        "message": "Hermes queue watchdog could not read the SQLite database.",
                    }
                ],
                "recommendations": [
                    {
                        "action": "inspect_database",
                        "confidence": 0.75,
                        "reason": str(exc),
                        "operator_prompt": "Check the Hermes issue-resolution DB path and schema before relying on queue health signals.",
                    }
                ],
            }

    if not args.no_log:
        append_log(args.log_path, record)

    if args.output == "json":
        print(json.dumps(record, indent=2, sort_keys=True))
    else:
        print(render_text(record))

    if args.fail_on_alert and record.get("alerts"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
