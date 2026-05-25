#!/usr/bin/env python3
"""Compare live Claude MCP registrations against the tracked Kyber registry."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = REPO_ROOT / "configs" / "mcp" / "servers.yaml"
EXPECTED_ACTIVE_STATUSES = {"active", "active_when_unreal_running"}


@dataclass
class LiveMcpServer:
    """Parsed Claude MCP server registration."""

    server_id: str
    status: str | None
    scope: str | None
    transport_type: str | None
    command: str | None
    args: list[str]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Path to the canonical MCP registry YAML.",
    )
    parser.add_argument(
        "--claude-bin",
        default="claude",
        help="Claude CLI binary to query.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit non-zero when missing servers or registration mismatches are found.",
    )
    return parser.parse_args()


def run_command(command: list[str]) -> str:
    """Run a command and return stdout or raise with stderr context."""
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return result.stdout


def load_registry(path: Path) -> dict[str, Any]:
    """Load the canonical registry YAML."""
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Registry at {path} did not contain a mapping.")
    return payload


def parse_live_server_ids(list_output: str) -> list[str]:
    """Parse top-level server ids from `claude mcp list` output."""
    server_ids: list[str] = []
    for line in list_output.splitlines():
        if not line or line.startswith(" "):
            continue
        if line.startswith("plugin:"):
            continue
        if ":" not in line:
            continue
        server_id = line.split(":", 1)[0].strip()
        if server_id:
            server_ids.append(server_id)
    return server_ids


def parse_key_value_blocks(raw_text: str) -> dict[str, str]:
    """Parse indented `Key: Value` blocks from Claude output."""
    parsed: dict[str, str] = {}
    current_key: str | None = None

    for line in raw_text.splitlines():
        if line.startswith("To remove this server"):
            break

        match = re.match(r"^\s{2,}([^:]+):\s*(.*)$", line)
        if match:
            current_key = match.group(1).strip()
            parsed[current_key] = match.group(2).strip()
            continue

        if current_key and line.strip():
            parsed[current_key] = f"{parsed[current_key]} {line.strip()}".strip()

    return parsed


def parse_live_server(server_id: str, get_output: str) -> LiveMcpServer:
    """Parse a single `claude mcp get` output block."""
    fields = parse_key_value_blocks(get_output)
    args_text = fields.get("Args", "").strip()
    args = args_text.split() if args_text else []

    return LiveMcpServer(
        server_id=server_id,
        status=fields.get("Status"),
        scope=fields.get("Scope"),
        transport_type=fields.get("Type"),
        command=fields.get("Command"),
        args=args,
    )


def load_live_servers(claude_bin: str) -> dict[str, LiveMcpServer]:
    """Load all live Claude MCP registrations."""
    list_output = run_command([claude_bin, "mcp", "list"])
    server_ids = parse_live_server_ids(list_output)
    live_servers: dict[str, LiveMcpServer] = {}
    for server_id in server_ids:
        get_output = run_command([claude_bin, "mcp", "get", server_id])
        live_servers[server_id] = parse_live_server(server_id, get_output)
    return live_servers


def expected_claude_servers(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the registry servers that should exist in Claude Code."""
    result: dict[str, dict[str, Any]] = {}
    for server in registry.get("servers", []):
        if not isinstance(server, dict):
            continue
        if "claude_code" not in server.get("client_surfaces", []):
            continue
        if server.get("status") not in EXPECTED_ACTIVE_STATUSES:
            continue
        server_id = server.get("id")
        if isinstance(server_id, str):
            result[server_id] = server
    return result


def normalize_registry_transport(transport: str | None) -> str | None:
    """Normalize registry transport labels to the client-visible Claude type."""
    if transport == "stdio_bridge_to_http":
        return "stdio"
    return transport


def compare_registry_to_live(
    registry_servers: dict[str, dict[str, Any]],
    live_servers: dict[str, LiveMcpServer],
) -> dict[str, Any]:
    """Compare live Claude registrations against the tracked registry."""
    missing_in_live = sorted(server_id for server_id in registry_servers if server_id not in live_servers)
    missing_in_registry = sorted(server_id for server_id in live_servers if server_id not in registry_servers)

    mismatches: list[dict[str, Any]] = []
    for server_id, registry_server in registry_servers.items():
        live_server = live_servers.get(server_id)
        if not live_server:
            continue

        registration = registry_server.get("registration", {})
        expected_transport = normalize_registry_transport(registry_server.get("transport"))
        expected_command = registration.get("command")
        expected_args = registration.get("args", []) or []

        if expected_transport and live_server.transport_type and expected_transport != live_server.transport_type:
            mismatches.append(
                {
                    "server_id": server_id,
                    "field": "transport",
                    "expected": expected_transport,
                    "actual": live_server.transport_type,
                }
            )
        if expected_command and live_server.command != expected_command:
            mismatches.append(
                {
                    "server_id": server_id,
                    "field": "command",
                    "expected": expected_command,
                    "actual": live_server.command,
                }
            )
        if list(expected_args) != live_server.args:
            mismatches.append(
                {
                    "server_id": server_id,
                    "field": "args",
                    "expected": list(expected_args),
                    "actual": live_server.args,
                }
            )

    return {
        "missing_in_live": missing_in_live,
        "missing_in_registry": missing_in_registry,
        "mismatches": mismatches,
        "live_servers": {
            server_id: {
                "status": live_server.status,
                "scope": live_server.scope,
                "type": live_server.transport_type,
                "command": live_server.command,
                "args": live_server.args,
            }
            for server_id, live_server in sorted(live_servers.items())
        },
    }


def render_text(summary: dict[str, Any]) -> str:
    """Render a human-readable sync summary."""
    lines = ["MCP registry sync summary"]

    live_servers = summary["live_servers"]
    lines.append(f"- Live Claude MCP servers: {', '.join(live_servers) if live_servers else 'none'}")

    if summary["missing_in_live"]:
        lines.append(f"- Missing in live Claude config: {', '.join(summary['missing_in_live'])}")
    else:
        lines.append("- Missing in live Claude config: none")

    if summary["missing_in_registry"]:
        lines.append(f"- Missing in registry: {', '.join(summary['missing_in_registry'])}")
    else:
        lines.append("- Missing in registry: none")

    if summary["mismatches"]:
        lines.append("- Registration mismatches:")
        for mismatch in summary["mismatches"]:
            lines.append(
                f"  - {mismatch['server_id']} {mismatch['field']}: expected={mismatch['expected']} actual={mismatch['actual']}"
            )
    else:
        lines.append("- Registration mismatches: none")

    return "\n".join(lines)


def main() -> int:
    """Run the registry sync check."""
    args = parse_args()
    registry = load_registry(args.registry)
    registry_servers = expected_claude_servers(registry)
    live_servers = load_live_servers(args.claude_bin)
    summary = compare_registry_to_live(registry_servers, live_servers)

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))

    has_drift = bool(summary["missing_in_live"] or summary["missing_in_registry"] or summary["mismatches"])
    return 1 if has_drift and args.fail_on_drift else 0


if __name__ == "__main__":
    sys.exit(main())