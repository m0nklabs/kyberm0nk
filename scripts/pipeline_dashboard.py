#!/usr/bin/env python3
"""
Pipeline Dashboard - Unified health view for kanban tasks and issue tracking.

Displays:
- Active kanban tasks with run history
- Kanban pipeline stage distribution
- Recent issue runs and failures
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

KANBAN_DB = Path.home() / ".hermes" / "kanban" / "kanban.db"
ISSUE_DB = Path.home() / ".hermes" / "issue_resolution.db"


def get_active_kanban_tasks():
    """Return active kanban tasks (status in ready/doing/claimed)."""
    # Use board-level cryptotrader DB which has the tasks table
    board_db = Path.home() / ".hermes" / "kanban" / "boards" / "cryptotrader" / "kanban.db"
    if not board_db.exists():
        return []

    conn = sqlite3.connect(str(board_db))
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, assignee, status, created_at, started_at,
               consecutive_failures, last_failure_error
        FROM tasks
        WHERE status IN ('ready', 'doing', 'claimed')
        ORDER BY started_at DESC, created_at DESC
        LIMIT 20
    """)
    rows = cur.fetchall()

    results = []
    for row in rows:
        task_id, title, assignee, status, created_at, started_at, failures, last_error = row

        started_str = ""
        if started_at:
            started_str = datetime.fromtimestamp(started_at).strftime("%Y-%m-%d %H:%M")

        results.append({
            'task_id': task_id,
            'title': title,
            'assignee': assignee or "unassigned",
            'status': status,
            'started_at': started_str,
            'consecutive_failures': failures,
            'last_error': last_error
        })

    conn.close()
    return results


def get_kanban_pipeline_state():
    """Return kanban tasks grouped by status from board-specific DB."""
    # Use board-level cryptotrader DB which has the tasks table
    board_db = Path.home() / ".hermes" / "kanban" / "boards" / "cryptotrader" / "kanban.db"
    if not board_db.exists():
        return {'stages': {}, 'stale_cards': []}

    conn = sqlite3.connect(str(board_db))
    cur = conn.cursor()

    # Status counts
    cur.execute("""
        SELECT status, COUNT(*)
        FROM tasks
        GROUP BY status
        ORDER BY status
    """)
    stages = dict(cur.fetchall())

    # Stale tasks (not updated in 7 days, not in terminal states)
    one_week_ago = int((datetime.now() - timedelta(days=7)).timestamp())
    cur.execute("""
        SELECT id, title, status, started_at, consecutive_failures
        FROM tasks
        WHERE started_at < ? AND status NOT IN ('done', 'failed', 'cancelled')
        ORDER BY started_at ASC
    """, (one_week_ago,))
    stale = cur.fetchall()

    conn.close()
    return {'stages': stages, 'stale_cards': stale}


def get_recent_issues():
    """Return recent issue runs from issue_resolution DB."""
    if not ISSUE_DB.exists():
        return []

    conn = sqlite3.connect(str(ISSUE_DB))
    cur = conn.cursor()

    # Get recent runs (last 7 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_ts = seven_days_ago.timestamp()

    cur.execute("""
        SELECT id, repo, issue_number, branch, status, pr_number, pr_url,
               error, created_at, updated_at, attempt_count, review_findings_count
        FROM issue_runs
        WHERE created_at > ?
        ORDER BY created_at DESC
        LIMIT 20
    """, (seven_days_ago_ts,))

    rows = cur.fetchall()
    results = []
    for row in rows:
        run_id, repo, issue_num, branch, status, pr_num, pr_url, error, created_at, updated_at, attempts, findings = row

        created_str = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M") if created_at else ""
        updated_str = datetime.fromtimestamp(updated_at).strftime("%Y-%m-%d %H:%M") if updated_at else ""

        results.append({
            'run_id': run_id,
            'repo': repo,
            'issue_number': issue_num,
            'branch': branch,
            'status': status,
            'pr_number': pr_num,
            'pr_url': pr_url,
            'error': error,
            'created_at': created_str,
            'updated_at': updated_str,
            'attempts': attempts,
            'findings': findings
        })

    conn.close()
    return results


def format_dashboard():
    """Format dashboard output for display."""
    lines = [
        "=" * 70,
        "PIPELINE HEALTH DASHBOARD",
        "=" * 70,
        ""
    ]

    # Active kanban tasks section
    lines.append("ACTIVE KANBAN TASKS")
    lines.append("-" * 70)
    try:
        tasks = get_active_kanban_tasks()
        if not tasks:
            lines.append("  No active tasks")
        else:
            for task in tasks:
                fail_str = ""
                if task['consecutive_failures'] > 0:
                    fail_str = f" | failures: {task['consecutive_failures']}"
                    if task['last_error']:
                        fail_str += f" ({task['last_error'][:40]})"

                lines.append(
                    f"  [{task['status']:8s}] {task['task_id'][:20]:20s} | "
                    f"{task['title'][:40]:40s} | {task['assignee']:12s}{fail_str}"
                )
    except Exception as e:
        lines.append(f"  Error reading kanban tasks: {e}")

    lines.append("")

    # Kanban pipeline stages section
    lines.append("KANBAN PIPELINE STAGES")
    lines.append("-" * 70)
    try:
        kanban_state = get_kanban_pipeline_state()
        stages = kanban_state.get('stages', {})
        if not stages:
            lines.append("  No kanban cards")
        else:
            for stage, count in sorted(stages.items()):
                lines.append(f"  {stage:25s}: {count:3d}")
    except Exception as e:
        lines.append(f"  Error reading pipeline stages: {e}")

    lines.append("")

    # Recent issues section
    lines.append("RECENT ISSUE RUNS (7 days)")
    lines.append("-" * 70)
    try:
        issues = get_recent_issues()
        if not issues:
            lines.append("  No recent issue runs")
        else:
            for issue in issues[:15]:
                pr_str = f"PR#{issue['pr_number']}" if issue['pr_number'] else "no PR"
                error_str = f" - {issue['error'][:50]}" if issue['error'] else ""

                lines.append(
                    f"  #{issue['issue_number']:4d} [{issue['status']:10s}] "
                    f"{issue['repo']:20s} | {pr_str} | {issue['created_at']} "
                    f"(attempts:{issue['attempts']}, findings:{issue['findings']}){error_str}"
                )
    except Exception as e:
        lines.append(f"  Error reading issue runs: {e}")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


if __name__ == "__main__":
    print(format_dashboard())
