#!/usr/bin/env python3
"""Generate README-activity.svg from the GitHub contribution calendar.

Fetches daily contribution counts through the GraphQL API (via the `gh` CLI,
which must be authenticated) and renders a line chart as a standalone SVG.
No third-party dependencies: only the Python standard library and `gh`.

Usage:
    python3 scripts/activity_graph.py --user Jfernandez27 --days 30 --output README-activity.svg
"""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

# Visual theme (inspired by the "merko" theme of github-readme-activity-graph)
WIDTH, HEIGHT = 1200, 420
PLOT_LEFT, PLOT_RIGHT, PLOT_TOP, PLOT_BOTTOM = 90, 1150, 80, 350
BG_COLOR = "#0a0f0b"
BORDER_COLOR = "#ffffff"
TEXT_COLOR = "#f6f8fa"
GRID_COLOR = "#f6f8fa"
LINE_COLOR = "#F97316"
POINT_COLOR = "#abd200"
FONT = "'Segoe UI', Ubuntu, Helvetica, Arial, sans-serif"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_days(user: str, start: date, end: date) -> list[tuple[date, int]]:
    """Return one (date, count) pair per day in [start, end], inclusive."""
    variables = {
        "login": user,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": f"{end.isoformat()}T23:59:59Z",
    }
    cmd = ["gh", "api", "graphql", "-f", f"query={QUERY}"]
    for key, value in variables.items():
        cmd += ["-f", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    counts = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            counts[date.fromisoformat(day["date"])] = day["contributionCount"]

    days = []
    current = start
    while current <= end:
        days.append((current, counts.get(current, 0)))
        current += timedelta(days=1)
    return days


def nice_step(max_value: int, target_ticks: int = 7) -> int:
    """Pick a readable Y-axis step so that there are roughly `target_ticks` gridlines."""
    if max_value <= 0:
        return 1
    raw = max_value / target_ticks
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000):
        if step >= raw:
            return step
    return int(raw)


def render(user: str, days: list[tuple[date, int]]) -> str:
    n = len(days)
    counts = [c for _, c in days]
    total = sum(counts)
    step = nice_step(max(counts))
    y_max = max(step, ((max(counts) + step - 1) // step) * step)

    plot_w = PLOT_RIGHT - PLOT_LEFT
    plot_h = PLOT_BOTTOM - PLOT_TOP
    x_gap = plot_w / (n - 1) if n > 1 else 0

    def x_at(i: int) -> float:
        return PLOT_LEFT + i * x_gap

    def y_at(value: int) -> float:
        return PLOT_BOTTOM - (value / y_max) * plot_h

    parts = [
        f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{user} contribution graph, last {n} days, {total} contributions">',
        f"<title>{user}'s Contribution Graph - last {n} days</title>",
        "<style>",
        f"  text {{ font-family: {FONT}; fill: {TEXT_COLOR}; }}",
        "  .title { font-size: 20px; font-weight: 600; }",
        "  .subtitle { font-size: 13px; opacity: .8; }",
        "  .label { font-size: 12px; }",
        "  .axis { font-size: 13px; font-weight: 500; }",
        f"  .grid {{ stroke: {GRID_COLOR}; stroke-opacity: .12; stroke-width: 1; }}",
        f"  .line {{ fill: none; stroke: {LINE_COLOR}; stroke-width: 3; "
        "stroke-linejoin: round; stroke-linecap: round; }",
        f"  .area {{ fill: {LINE_COLOR}; fill-opacity: .12; }}",
        f"  .point {{ fill: {POINT_COLOR}; stroke: {BG_COLOR}; stroke-width: 1.5; }}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" '
        f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1"/>',
        f'<text x="{PLOT_LEFT}" y="36" class="title">{user}\'s Contribution Graph</text>',
        f'<text x="{PLOT_LEFT}" y="58" class="subtitle">Last {n} days · {total} contributions '
        f'· {days[0][0].strftime("%b %d")} – {days[-1][0].strftime("%b %d, %Y")}</text>',
    ]

    # Horizontal gridlines and Y labels
    value = 0
    while value <= y_max:
        y = y_at(value)
        parts.append(f'<line class="grid" x1="{PLOT_LEFT}" x2="{PLOT_RIGHT}" y1="{y:.2f}" y2="{y:.2f}"/>')
        parts.append(f'<text x="{PLOT_LEFT - 12}" y="{y + 4:.2f}" class="label" text-anchor="end">{value}</text>')
        value += step

    # Vertical gridlines and X labels (day of month)
    for i, (d, _) in enumerate(days):
        x = x_at(i)
        parts.append(f'<line class="grid" x1="{x:.2f}" x2="{x:.2f}" y1="{PLOT_TOP}" y2="{PLOT_BOTTOM}"/>')
        parts.append(f'<text x="{x:.2f}" y="{PLOT_BOTTOM + 22}" class="label" text-anchor="middle">{d.day}</text>')

    # Axis titles
    parts.append(f'<text x="{(PLOT_LEFT + PLOT_RIGHT) / 2:.0f}" y="{HEIGHT - 16}" class="axis" text-anchor="middle">Days</text>')
    parts.append(f'<text transform="translate(28 {(PLOT_TOP + PLOT_BOTTOM) / 2:.0f}) rotate(-90)" '
                 'class="axis" text-anchor="middle">Contributions</text>')

    # Area, line and points
    line_points = " ".join(f"{x_at(i):.2f},{y_at(c):.2f}" for i, c in enumerate(counts))
    area_points = f"{PLOT_LEFT},{PLOT_BOTTOM} {line_points} {x_at(n - 1):.2f},{PLOT_BOTTOM}"
    parts.append(f'<polygon class="area" points="{area_points}"/>')
    parts.append(f'<polyline class="line" points="{line_points}"/>')
    for i, (d, c) in enumerate(days):
        parts.append(f'<circle class="point" cx="{x_at(i):.2f}" cy="{y_at(c):.2f}" r="4">'
                     f"<title>{d.isoformat()}: {c} contributions</title></circle>")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--user", required=True, help="GitHub login")
    parser.add_argument("--days", type=int, default=30, help="number of days to plot (default: 30)")
    parser.add_argument("--output", default="README-activity.svg", help="output SVG path")
    args = parser.parse_args()

    if args.days < 2:
        parser.error("--days must be at least 2")

    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=args.days - 1)

    try:
        days = fetch_days(args.user, start, today)
    except subprocess.CalledProcessError as exc:
        print(f"gh api failed: {exc.stderr.strip()}", file=sys.stderr)
        return 1

    svg = render(args.user, days)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {args.output}: {len(days)} days, {sum(c for _, c in days)} contributions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
