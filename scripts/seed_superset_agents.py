#!/usr/bin/env python3
"""Seed KyberM0nk terminal-agent rows into a local Superset host database."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class AgentConfig:
    """Terminal-agent launch configuration stored by Superset host-service."""

    preset_id: str
    label: str
    command: str
    args: list[str]
    prompt_transport: str
    prompt_args: list[str]
    env: dict[str, str]


def repo_root() -> Path:
    """Return the KyberM0nk repository root."""

    return Path(__file__).resolve().parents[1]


def default_home() -> Path:
    """Return the Superset home directory used by Kyber."""

    configured = os.environ.get("SUPERSET_HOME_DIR")
    if configured:
        return Path(configured).expanduser()
    return repo_root() / "tmp" / "superset-home"


def agent_configs(include_claude_code: bool) -> list[AgentConfig]:
    """Build the Kyber agent configs to seed."""

    root = repo_root()
    configs = [
        AgentConfig(
            preset_id="kyber-opencode",
            label="Kyber OpenCode (Guardian)",
            command=str(root / "scripts" / "superset-opencode-agent.sh"),
            args=[],
            prompt_transport="stdin",
            prompt_args=[],
            env={},
        ),
        AgentConfig(
            preset_id="kyber-aider",
            label="Kyber Aider (Guardian)",
            command=str(root / "scripts" / "superset-aider-agent.sh"),
            args=[],
            prompt_transport="stdin",
            prompt_args=[],
            env={},
        ),
    ]

    if include_claude_code:
        configs.append(
            AgentConfig(
                preset_id="kyber-claude-code",
                label="Claude Code (Premium)",
                command="claude",
                args=["--permission-mode", "acceptEdits"],
                prompt_transport="argv",
                prompt_args=[],
                env={},
            )
        )

    return configs


def find_host_databases(home: Path) -> list[Path]:
    """Find Superset host databases below a Superset home directory."""

    host_root = home / "host"
    if not host_root.exists():
        return []
    return sorted(path for path in host_root.glob("*/host.db") if path.is_file())


def table_exists(connection: sqlite3.Connection) -> bool:
    """Return whether the target Superset agent table exists."""

    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        ("host_agent_configs",),
    ).fetchone()
    return row is not None


def existing_row_count(connection: sqlite3.Connection) -> int:
    """Return the number of configured Superset terminal agents."""

    row = connection.execute("SELECT COUNT(*) FROM host_agent_configs").fetchone()
    return int(row[0]) if row else 0


def next_display_order(connection: sqlite3.Connection) -> int:
    """Return the next display order for a new Superset agent row."""

    row = connection.execute(
        "SELECT COALESCE(MAX(display_order), -1) + 1 FROM host_agent_configs"
    ).fetchone()
    return int(row[0]) if row else 0


def upsert_config(
    connection: sqlite3.Connection,
    config: AgentConfig,
    dry_run: bool,
) -> str:
    """Insert or update one Superset agent row and return the action taken."""

    existing = connection.execute(
        "SELECT id FROM host_agent_configs WHERE preset_id = ? ORDER BY display_order LIMIT 1",
        (config.preset_id,),
    ).fetchone()
    now = int(time.time() * 1000)
    args_json = json.dumps(config.args)
    prompt_args_json = json.dumps(config.prompt_args)
    env_json = json.dumps(config.env)

    if existing:
        if not dry_run:
            connection.execute(
                """
                UPDATE host_agent_configs
                SET label = ?, command = ?, args_json = ?, prompt_transport = ?,
                    prompt_args_json = ?, env_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    config.label,
                    config.command,
                    args_json,
                    config.prompt_transport,
                    prompt_args_json,
                    env_json,
                    now,
                    existing[0],
                ),
            )
        return "updated"

    if not dry_run:
        connection.execute(
            """
            INSERT INTO host_agent_configs (
                id, preset_id, label, command, args_json, prompt_transport,
                prompt_args_json, env_json, display_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                config.preset_id,
                config.label,
                config.command,
                args_json,
                config.prompt_transport,
                prompt_args_json,
                env_json,
                next_display_order(connection),
                now,
                now,
            ),
        )
    return "inserted"


def seed_database(
    database_path: Path,
    configs: Sequence[AgentConfig],
    dry_run: bool,
) -> list[str]:
    """Seed all Kyber agent configs into one Superset host database."""

    with sqlite3.connect(database_path) as connection:
        if not table_exists(connection):
            return [f"skipped {database_path}: host_agent_configs table is missing"]
        if existing_row_count(connection) == 0:
            return [
                f"skipped {database_path}: default Superset agents are not seeded yet; run scripts/superset.sh agents first"
            ]

        messages = []
        for config in configs:
            action = upsert_config(connection, config, dry_run=dry_run)
            messages.append(f"{action} {config.preset_id} in {database_path}")
        if dry_run:
            connection.rollback()
        else:
            connection.commit()
        return messages


def include_claude_code(mode: str) -> bool:
    """Resolve whether the optional Claude Code config should be seeded."""

    if mode == "always":
        return True
    if mode == "never":
        return False
    return shutil.which("claude") is not None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=default_home())
    parser.add_argument("--db", type=Path, action="append", default=[])
    parser.add_argument(
        "--include-claude-code",
        choices=["auto", "always", "never"],
        default="auto",
        help="Seed Claude Code only when installed by default.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Superset agent seeder."""

    args = parse_args(argv)
    databases = [path.expanduser() for path in args.db] or find_host_databases(
        args.home.expanduser()
    )
    if not databases:
        print(
            f"No Superset host databases found under {args.home}. Run scripts/superset.sh login/start first."
        )
        return 1

    configs = agent_configs(include_claude_code(args.include_claude_code))
    all_messages: list[str] = []
    for database_path in databases:
        all_messages.extend(seed_database(database_path, configs, dry_run=args.dry_run))

    for message in all_messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
