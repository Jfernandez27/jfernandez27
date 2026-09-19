#!/usr/bin/env python3
"""Build the profile statistics badges (badges/*.svg) with Shields.io.

Metrics come from the GitHub GraphQL API through the `gh` CLI, which must be
authenticated. Commit, PR and issue contributions and streaks are computed
across every year of the account, not just the last 12 months. No third-party
dependencies.

Usage:
    python3 scripts/build_badges.py --user Jfernandez27 --output-dir badges
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LABEL_COLOR = "101010"
STYLE = "flat"

# Repository topics counted as frameworks. Languages are excluded on purpose:
# the Languages badge already covers them (via Linguist).
FRAMEWORK_TOPICS = [
    "laravel", "laravel-framework", "livewire", "filament",
    "react", "reactjs", "nextjs", "vue", "vuejs", "nuxt",
    "express", "nestjs", "django", "fastapi", "flask", "tailwindcss",
]

# Linguist "languages" that are markup, styling or config rather than code.
NON_CODE_LANGUAGES = {
    "CSS", "SCSS", "Sass", "Less", "HTML", "Blade", "EJS", "MDX", "Markdown",
    "Dockerfile", "Makefile", "Procfile", "Nix", "Vim Script", "Batchfile",
}

# Featured projects: (badge slug, repository name). One "last activity" badge
# is produced per entry, named activity-<slug>.svg.
PROJECT_REPOS = [
    ("edupro360", "EduPro360"),
    ("apexfit", "apexfit"),
    ("tepuy", "tepuy"),
    ("ollama-dev-env", "ollama-dev-env"),
]

PROFILE_QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    starredRepositories { totalCount }
    contributionsCollection { contributionYears }
    repositories(ownerAffiliations: [OWNER], isFork: false, first: 100) {
      totalCount
      nodes {
        languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
        repositoryTopics(first: 10) { nodes { topic { name } } }
      }
    }
  }
}
"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

REPO_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) { pushedAt }
}
"""


def graphql(query: str, **variables) -> dict:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        cmd += ["-f", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def streaks(daily: dict[date, int], today: date) -> tuple[int, int]:
    """Return (current streak, longest streak) in days with >0 contributions."""
    longest = run = 0
    for day in sorted(daily):
        run = run + 1 if daily[day] > 0 else 0
        longest = max(longest, run)

    # The current streak may still be alive if today has no contribution yet.
    cursor = today if daily.get(today, 0) > 0 else today - timedelta(days=1)
    current = 0
    while daily.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def humanize_age(pushed_at: str, now: datetime) -> str:
    delta = now - datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
    days = delta.days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    if days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"


def activity_color(pushed_at: str, now: datetime) -> str:
    days = (now - datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))).days
    if days < 30:
        return "22C55E"  # green: active
    if days < 180:
        return "FACC15"  # yellow: slowing down
    return "9CA3AF"  # grey: dormant


def collect_metrics(user: str) -> dict:
    now = datetime.now(timezone.utc)
    today = now.date()
    profile = graphql(PROFILE_QUERY, login=user)["user"]
    repos = profile["repositories"]["nodes"]

    language_sizes = Counter()
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name not in NON_CODE_LANGUAGES:
                language_sizes[name] += edge["size"]
    top_languages = [name for name, _ in language_sizes.most_common(3)]

    topic_counts = Counter()
    for repo in repos:
        for node in repo["repositoryTopics"]["nodes"]:
            topic = node["topic"]["name"]
            if topic in FRAMEWORK_TOPICS:
                topic_counts[topic] += 1
    top_frameworks = [name for name, _ in topic_counts.most_common(3)]

    commits = prs = issues = 0
    daily: dict[date, int] = {}
    for year in profile["contributionsCollection"]["contributionYears"]:
        yearly = graphql(
            YEAR_QUERY, login=user,
            **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"},
        )["user"]["contributionsCollection"]
        commits += yearly["totalCommitContributions"]
        prs += yearly["totalPullRequestContributions"]
        issues += yearly["totalIssueContributions"]
        for week in yearly["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                d = date.fromisoformat(day["date"])
                if d <= today:
                    daily[d] = day["contributionCount"]
    current_streak, longest_streak = streaks(daily, today)

    projects = {}
    for slug, repo_name in PROJECT_REPOS:
        pushed_at = graphql(REPO_QUERY, owner=user, name=repo_name)["repository"]["pushedAt"]
        projects[slug] = (humanize_age(pushed_at, now), activity_color(pushed_at, now))

    return {
        "repositories": profile["repositories"]["totalCount"],
        "commits": commits,
        "prs": prs,
        "issues": issues,
        "followers": profile["followers"]["totalCount"],
        "starred": profile["starredRepositories"]["totalCount"],
        "languages": " | ".join(top_languages) or "n/a",
        "frameworks": " | ".join(top_frameworks) or "Add topics on GitHub",
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "projects": projects,
    }


def shields_url(label: str, message: str, color: str) -> str:
    def escape(text: str) -> str:
        # Shields.io path syntax: "-" and "_" are separators, so they must be doubled.
        return urllib.parse.quote(text.replace("-", "--").replace("_", "__"), safe="")
    return (
        f"https://img.shields.io/badge/{escape(label)}-{escape(message)}-{color}"
        f"?style={STYLE}&labelColor={LABEL_COLOR}"
    )


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "profile-badges/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
    if b"<svg" not in body[:200]:
        raise RuntimeError(f"unexpected response from {url}: {body[:120]!r}")
    target.write_bytes(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--user", required=True, help="GitHub login")
    parser.add_argument("--output-dir", default="badges", help="directory for the SVG files")
    args = parser.parse_args()

    try:
        metrics = collect_metrics(args.user)
    except subprocess.CalledProcessError as exc:
        print(f"gh api failed: {exc.stderr.strip()}", file=sys.stderr)
        return 1

    def days(n: int) -> str:
        return f"{n} day{'s' if n != 1 else ''}"

    badges = [
        ("public-repos.svg", "Repositories", str(metrics["repositories"]), "0EA5E9"),
        ("total-commits.svg", "Total Commits", str(metrics["commits"]), "10B981"),
        ("pr-contrib.svg", "PR Contributions", str(metrics["prs"]), "22C55E"),
        ("issue-contrib.svg", "Issue Contributions", str(metrics["issues"]), "DC2626"),
        ("followers.svg", "Followers", str(metrics["followers"]), "FACC15"),
        ("starred.svg", "Starred Repositories", str(metrics["starred"]), "F97316"),
        ("languages.svg", "Languages", metrics["languages"], "D946EF"),
        ("frameworks.svg", "Frameworks", metrics["frameworks"], "8B5CF6"),
        ("current-streak.svg", "Current Streak", days(metrics["current_streak"]), "F97316"),
        ("longest-streak.svg", "Longest Streak", days(metrics["longest_streak"]), "EF4444"),
        ("updated.svg", "Profile updated", datetime.now(timezone.utc).strftime("%Y-%m-%d"), "6B7280"),
    ]
    for slug, (age, color) in metrics["projects"].items():
        badges.append((f"activity-{slug}.svg", "Last push", age, color))

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for filename, label, message, color in badges:
        download(shields_url(label, message, color), out / filename)
        print(f"{filename}: {label} = {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
