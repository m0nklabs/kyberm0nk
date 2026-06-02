#!/usr/bin/env python3
"""Guard managed repositories against direct main/master implementation drift.

This script is intentionally read-only. It fails when a managed repository is on
its protected branch with local implementation drift, because Kyber/Hermes work
must flow through issue -> feature branch -> PR -> review -> manual merge.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_MANAGED_REPOS = [
    {
        "name": "CryptoTrader",
        "path": "/home/flip/cryptotrader_hermes",
        "remote": "m0nklabs/cryptotrader",
        "protected_branches": ["master", "main"],
        "allowed_dirty_prefixes": [
            ".aider.chat.history.md",
            ".aider.input.history",
            ".aider.tags.cache.v4/",
        ],
    }
]


@dataclass(frozen=True)
class RepoConfig:
    """Configuration for one managed repository guard."""

    name: str
    path: Path
    remote: str
    protected_branches: tuple[str, ...]
    allowed_dirty_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class RepoStatus:
    """Read-only status for one managed repository."""

    name: str
    path: str
    remote: str
    branch: str | None
    protected: bool
    clean: bool
    violating_paths: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    ok: bool
    reason: str


def run_git(path: Path, *args: str) -> str:
    """Run a git command in a repository and return stdout."""

    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git -C {path} {' '.join(args)} failed: {stderr}")
    return result.stdout


def normalize_status_path(line: str) -> str:
    """Extract the path portion from git status --porcelain output."""

    raw = line[3:] if len(line) > 3 else line
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.strip()


def is_allowed(path: str, prefixes: tuple[str, ...]) -> bool:
    """Return true when a dirty path is local tool noise allowed by policy."""

    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in prefixes)


def inspect_repo(config: RepoConfig) -> RepoStatus:
    """Inspect one managed repository without mutating it."""

    if not config.path.exists():
        return RepoStatus(
            name=config.name,
            path=str(config.path),
            remote=config.remote,
            branch=None,
            protected=False,
            clean=False,
            violating_paths=("<missing repository path>",),
            ignored_paths=(),
            ok=False,
            reason="repository path does not exist",
        )

    branch = run_git(config.path, "branch", "--show-current").strip() or None
    protected = branch in config.protected_branches if branch else False
    lines = [line for line in run_git(config.path, "status", "--porcelain").splitlines() if line.strip()]
    dirty_paths = [normalize_status_path(line) for line in lines]
    ignored = tuple(path for path in dirty_paths if is_allowed(path, config.allowed_dirty_prefixes))
    violating = tuple(path for path in dirty_paths if not is_allowed(path, config.allowed_dirty_prefixes))

    if protected and violating:
        ok = False
        reason = f"protected branch {branch!r} has implementation drift"
    else:
        ok = True
        if protected and ignored:
            reason = f"protected branch {branch!r} has only allowed local tool noise"
        elif protected:
            reason = f"protected branch {branch!r} is clean"
        elif violating:
            reason = f"feature branch {branch!r} has local changes"
        else:
            reason = f"branch {branch!r} is clean"

    return RepoStatus(
        name=config.name,
        path=str(config.path),
        remote=config.remote,
        branch=branch,
        protected=protected,
        clean=not dirty_paths,
        violating_paths=violating,
        ignored_paths=ignored,
        ok=ok,
        reason=reason,
    )


def load_configs(config_path: Path | None) -> list[RepoConfig]:
    """Load managed repository configs from JSON or use defaults."""

    if config_path is None:
        raw: list[dict[str, Any]] = DEFAULT_MANAGED_REPOS
    else:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        repos = payload.get("repos") if isinstance(payload, dict) else payload
        if not isinstance(repos, list):
            raise ValueError("managed repo config must be a list or an object with repos")
        raw = [repo for repo in repos if isinstance(repo, dict)]

    configs: list[RepoConfig] = []
    for entry in raw:
        configs.append(
            RepoConfig(
                name=str(entry["name"]),
                path=Path(str(entry["path"])).expanduser(),
                remote=str(entry.get("remote") or ""),
                protected_branches=tuple(str(value) for value in entry.get("protected_branches", ["main", "master"])),
                allowed_dirty_prefixes=tuple(str(value) for value in entry.get("allowed_dirty_prefixes", [])),
            )
        )
    return configs


def render_text(statuses: list[RepoStatus]) -> str:
    """Render compact human-readable status."""

    lines: list[str] = []
    for status in statuses:
        verdict = "OK" if status.ok else "VIOLATION"
        lines.append(f"{verdict} {status.name}: {status.reason}")
        if status.violating_paths:
            for path in status.violating_paths:
                lines.append(f"  - {path}")
        if status.ignored_paths:
            lines.append(f"  ignored local noise: {', '.join(status.ignored_paths)}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Optional JSON config with managed repos.")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        statuses = [inspect_repo(config) for config in load_configs(args.config)]
    except Exception as exc:
        print(f"managed repo guard failed: {exc}", file=sys.stderr)
        return 2

    if args.output == "json":
        print(json.dumps([status.__dict__ for status in statuses], indent=2, sort_keys=True))
    else:
        print(render_text(statuses))

    return 0 if all(status.ok for status in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
