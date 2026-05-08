#!/usr/bin/env python3
"""Render Guardian benchmark CSV trend charts as a standalone HTML report."""

from __future__ import annotations

import argparse
import csv
import html
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "guardian-context-benchmarks"


@dataclass(frozen=True)
class Point:
    """One plotted data point."""

    x: float
    y: float
    label: str


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    """Read a benchmark CSV file."""
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str, default: float = 0.0) -> float:
    """Parse a numeric CSV field."""
    raw_value = row.get(key, "")
    if raw_value in {"", "None", None}:
        return default
    try:
        return float(raw_value)
    except ValueError:
        return default


def integer(row: dict[str, str], key: str, default: int = 0) -> int:
    """Parse an integer CSV field."""
    return int(number(row, key, float(default)))


def scale(value: float, domain_min: float, domain_max: float, range_min: float, range_max: float) -> float:
    """Scale a value from one range into another."""
    if math.isclose(domain_min, domain_max):
        return (range_min + range_max) / 2
    ratio = (value - domain_min) / (domain_max - domain_min)
    return range_min + (ratio * (range_max - range_min))


def axis_ticks(domain_min: float, domain_max: float, count: int = 5) -> list[float]:
    """Generate simple evenly spaced axis ticks."""
    if count <= 1:
        return [domain_min]
    return [domain_min + ((domain_max - domain_min) * index / (count - 1)) for index in range(count)]


def fmt(value: float) -> str:
    """Format chart labels compactly."""
    if abs(value) >= 1000:
        return f"{value / 1000:.0f}k"
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def chart_frame(title: str, x_label: str, y_label: str, x_values: list[float], y_values: list[float]) -> tuple[list[str], dict[str, float]]:
    """Create an SVG chart frame and return plotting bounds."""
    width = 1080
    height = 320
    margin_left = 82
    margin_right = 28
    margin_top = 44
    margin_bottom = 62
    x_min = min(x_values) if x_values else 0
    x_max = max(x_values) if x_values else 1
    y_min = 0
    y_max = max(y_values) if y_values else 1
    if math.isclose(y_max, 0):
        y_max = 1
    y_max *= 1.12

    parts = [
        f'<g class="chart">',
        f'<text class="chart-title" x="{margin_left}" y="24">{html.escape(title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}"/>',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}"/>',
    ]

    for tick in axis_ticks(x_min, x_max):
        x = scale(tick, x_min, x_max, margin_left, width - margin_right)
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom}"/>')
        parts.append(f'<text class="tick" x="{x:.1f}" y="{height - 36}" text-anchor="middle">{fmt(tick)}</text>')

    for tick in axis_ticks(y_min, y_max):
        y = scale(tick, y_min, y_max, height - margin_bottom, margin_top)
        parts.append(f'<line class="grid" x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{margin_left - 10}" y="{y + 4:.1f}" text-anchor="end">{fmt(tick)}</text>')

    parts.append(f'<text class="axis-label" x="{width / 2:.1f}" y="{height - 10}" text-anchor="middle">{html.escape(x_label)}</text>')
    parts.append(
        f'<text class="axis-label" x="18" y="{height / 2:.1f}" text-anchor="middle" transform="rotate(-90 18 {height / 2:.1f})">{html.escape(y_label)}</text>'
    )
    bounds = {
        "width": width,
        "height": height,
        "left": margin_left,
        "right": width - margin_right,
        "top": margin_top,
        "bottom": height - margin_bottom,
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
    }
    return parts, bounds


def render_line_chart(title: str, x_label: str, y_label: str, series: dict[str, list[Point]]) -> str:
    """Render a multi-series SVG line chart."""
    x_values = [point.x for points in series.values() for point in points]
    y_values = [point.y for points in series.values() for point in points]
    parts, bounds = chart_frame(title, x_label, y_label, x_values, y_values)
    colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#ea580c", "#0891b2"]

    for index, (name, points) in enumerate(series.items()):
        color = colors[index % len(colors)]
        sorted_points = sorted(points, key=lambda point: point.x)
        path_points = []
        for point in sorted_points:
            x = scale(point.x, bounds["x_min"], bounds["x_max"], bounds["left"], bounds["right"])
            y = scale(point.y, bounds["y_min"], bounds["y_max"], bounds["bottom"], bounds["top"])
            path_points.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{color}"><title>{html.escape(point.label)}</title></circle>')
        if len(path_points) > 1:
            parts.append(f'<polyline class="line" stroke="{color}" points="{" ".join(path_points)}"/>')
        legend_x = bounds["left"] + (index * 170)
        parts.append(f'<circle cx="{legend_x}" cy="304" r="4" fill="{color}"/>')
        parts.append(f'<text class="legend" x="{legend_x + 10}" y="308">{html.escape(name)}</text>')

    parts.append("</g>")
    return "\n".join(parts)


def render_risk_map(rows: list[dict[str, str]]) -> str:
    """Render long-decode status grid by context and output cap."""
    filtered = [row for row in rows if row.get("task") == "long-decode"]
    inputs = sorted({integer(row, "target_context_tokens") for row in filtered})
    outputs = sorted({integer(row, "max_output_tokens") for row in filtered})
    modes = ["disabled", "enabled"]
    width = 1080
    cell_w = 54
    cell_h = 26
    left = 140
    top = 54
    block_gap = 48
    height = top + ((len(inputs) * cell_h) + block_gap) * len(modes) + 52
    status_color = {
        "ok": "#16a34a",
        "http-error": "#dc2626",
        "timeout": "#ea580c",
        "url-error": "#ea580c",
        "error": "#991b1b",
        "skipped": "#94a3b8",
    }
    by_key = {
        (
            integer(row, "target_context_tokens"),
            integer(row, "max_output_tokens"),
            row.get("thinking_mode", ""),
        ): row
        for row in filtered
    }

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Long decode risk map">',
        SVG_STYLE,
        '<text class="chart-title" x="32" y="28">Long Decode Risk Map</text>',
    ]
    for col, output in enumerate(outputs):
        x = left + col * cell_w + cell_w / 2
        parts.append(f'<text class="tick" x="{x:.1f}" y="48" text-anchor="middle">{output}</text>')
    parts.append(f'<text class="axis-label" x="{left + (len(outputs) * cell_w) / 2:.1f}" y="20" text-anchor="middle">max output tokens</text>')

    for mode_index, mode in enumerate(modes):
        y_offset = top + mode_index * ((len(inputs) * cell_h) + block_gap)
        parts.append(f'<text class="axis-label" x="32" y="{y_offset + 15}">{mode} thinking</text>')
        for row_index, target in enumerate(inputs):
            y = y_offset + row_index * cell_h
            parts.append(f'<text class="tick" x="{left - 10}" y="{y + 17}" text-anchor="end">{fmt(target)}</text>')
            for col, output in enumerate(outputs):
                x = left + col * cell_w
                row = by_key.get((target, output, mode))
                status = row.get("status", "missing") if row else "missing"
                color = status_color.get(status, "#e2e8f0")
                label = f"input={target} output={output} thinking={mode} status={status}"
                if row and row.get("elapsed_seconds"):
                    label += f" elapsed={row['elapsed_seconds']}s"
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" rx="4" fill="{color}"><title>{html.escape(label)}</title></rect>')

    legend_y = height - 22
    for index, (status, color) in enumerate([("ok", "#16a34a"), ("http-error", "#dc2626"), ("skipped", "#94a3b8"), ("missing", "#e2e8f0")]):
        x = 32 + index * 140
        parts.append(f'<rect x="{x}" y="{legend_y - 12}" width="18" height="18" rx="4" fill="{color}"/>')
        parts.append(f'<text class="legend" x="{x + 26}" y="{legend_y + 2}">{status}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def marker_prefill_series(rows: list[dict[str, str]]) -> dict[str, list[Point]]:
    """Build prefill latency trend from marker cap-32 rows."""
    series: dict[str, list[Point]] = defaultdict(list)
    for row in rows:
        if row.get("task") != "marker" or integer(row, "max_output_tokens") != 32 or row.get("status") != "ok":
            continue
        mode = row.get("thinking_mode", "unknown")
        prompt_tokens = number(row, "usage_prompt_tokens") or number(row, "target_context_tokens")
        elapsed = number(row, "elapsed_seconds")
        series[mode].append(Point(prompt_tokens, elapsed, f"{mode}: {prompt_tokens:.0f} prompt tokens, {elapsed:.1f}s"))
    return dict(series)


def long_decode_elapsed_series(rows: list[dict[str, str]]) -> dict[str, list[Point]]:
    """Build elapsed trend for successful long-decode rows."""
    series: dict[str, list[Point]] = defaultdict(list)
    for row in rows:
        if row.get("task") != "long-decode" or row.get("status") != "ok":
            continue
        completion = number(row, "usage_completion_tokens")
        if completion < 512:
            continue
        mode = row.get("thinking_mode", "unknown")
        prompt_tokens = integer(row, "usage_prompt_tokens", integer(row, "target_context_tokens"))
        elapsed = number(row, "elapsed_seconds")
        name = f"{mode}, prompt~{round(prompt_tokens / 1000):.0f}k"
        series[name].append(Point(completion, elapsed, f"{name}: {completion:.0f} completion tokens, {elapsed:.1f}s"))
    return dict(series)


def throughput_series(rows: list[dict[str, str]]) -> dict[str, list[Point]]:
    """Build tokens-per-second trend for long-decode rows."""
    series: dict[str, list[Point]] = defaultdict(list)
    for row in rows:
        if row.get("task") != "long-decode" or row.get("status") != "ok":
            continue
        completion = number(row, "usage_completion_tokens")
        elapsed = number(row, "elapsed_seconds")
        if completion < 1024 or elapsed <= 0:
            continue
        mode = row.get("thinking_mode", "unknown")
        output_cap = integer(row, "max_output_tokens")
        if output_cap not in {4096, 8192, 16384}:
            continue
        prompt_tokens = number(row, "usage_prompt_tokens") or number(row, "target_context_tokens")
        tokens_per_second = completion / elapsed
        name = f"{mode} cap={output_cap}"
        series[name].append(
            Point(prompt_tokens, tokens_per_second, f"{name}: prompt {prompt_tokens:.0f}, {tokens_per_second:.1f} tok/s")
        )
    return dict(series)


def build_summary(rows: list[dict[str, str]]) -> list[str]:
    """Build compact text summary bullets for the report."""
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    by_input: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_input[integer(row, "target_context_tokens")].append(row)

    bullets = [
        f"Rows analyzed: {len(rows)} ({', '.join(f'{key}: {value}' for key, value in sorted(status_counts.items()))}).",
    ]
    for target, group in sorted(by_input.items()):
        ok_rows = [row for row in group if row.get("status") == "ok"]
        long_rows = [row for row in ok_rows if row.get("task") == "long-decode"]
        max_completion = max((integer(row, "usage_completion_tokens") for row in long_rows), default=0)
        max_cap = max((integer(row, "max_output_tokens") for row in ok_rows), default=0)
        failures = [row for row in group if row.get("status") not in {"ok", "skipped"}]
        bullets.append(
            f"Input {target}: {len(ok_rows)}/{len(group)} ok, max ok cap {max_cap}, max observed long decode {max_completion} tokens, failures {len(failures)}."
        )
    return bullets


SVG_STYLE = """
<style>
  svg { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #0f172a; }
  .chart-title { font-size: 18px; font-weight: 700; fill: #0f172a; }
  .axis, .grid { stroke: #cbd5e1; stroke-width: 1; }
  .grid { opacity: 0.65; }
  .tick, .legend { font-size: 12px; fill: #475569; }
  .axis-label { font-size: 13px; font-weight: 600; fill: #334155; }
  .line { fill: none; stroke-width: 2.5; opacity: 0.9; }
</style>
"""


def render_report(csv_path: Path, output_path: Path) -> Path:
    """Render the complete trend report."""
    rows = read_rows(csv_path)
    prefill = render_line_chart(
        "Prompt Prefill Trend (marker, cap=32)",
        "prompt tokens",
        "elapsed seconds",
        marker_prefill_series(rows),
    )
    decode_elapsed = render_line_chart(
        "Long Decode Elapsed Time",
        "generated completion tokens",
        "elapsed seconds",
        long_decode_elapsed_series(rows),
    )
    throughput = render_line_chart(
        "Long Decode Throughput",
        "prompt tokens",
        "completion tokens/sec",
        throughput_series(rows),
    )
    risk_map = render_risk_map(rows)
    bullets = "\n".join(f"<li>{html.escape(bullet)}</li>" for bullet in build_summary(rows))

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Guardian Benchmark Trends</title>
  <style>
    body {{ margin: 0; background: #e5e7eb; color: #0f172a; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 28px; }}
    section {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 18px; overflow: hidden; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 10px; font-size: 18px; }}
    p, li {{ line-height: 1.45; }}
    .intro {{ margin-bottom: 18px; }}
    .summary {{ padding: 20px 24px; }}
    svg {{ display: block; width: 100%; height: auto; }}
    code {{ background: #e2e8f0; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <main>
    <div class="intro">
      <h1>Guardian Benchmark Trends</h1>
      <p>Source: <code>{html.escape(str(csv_path))}</code></p>
    </div>
    <section class="summary">
      <h2>Current Read</h2>
      <ul>{bullets}</ul>
    </section>
    <section><svg viewBox="0 0 1080 320">{SVG_STYLE}{prefill}</svg></section>
    <section><svg viewBox="0 0 1080 320">{SVG_STYLE}{decode_elapsed}</svg></section>
    <section><svg viewBox="0 0 1080 320">{SVG_STYLE}{throughput}</svg></section>
    <section>{risk_map}</section>
  </main>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    """Create CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Benchmark CSV file to render.")
    parser.add_argument("--output", type=Path, help="Output HTML report path.")
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_arg_parser()
    args = parser.parse_args()
    csv_path = args.csv_path.resolve()
    if not csv_path.exists():
        parser.error(f"CSV file does not exist: {csv_path}")

    output_path = args.output
    if output_path is None:
        output_path = csv_path.with_name(f"{csv_path.stem}_trends.html")
    render_report(csv_path, output_path.resolve())
    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())