"""Health score algorithm and recommendation engine for DevSkillMapper."""

import math
from datetime import datetime, timezone

from github_client import search_repos

# ── Configurable weights for the six health dimensions ────────────────
W_ACTIVITY = 0.20
W_COMMUNITY = 0.20
W_DOCUMENTATION = 0.15
W_SCALE = 0.15
W_STABILITY = 0.15
W_IMPACT = 0.15

GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (0, "D"),
]


# ── Helpers ───────────────────────────────────────────────────────────


def _normalize(value: float, max_val: float, scale: float = 100.0) -> float:
    """Clamp a value between 0 and *scale* after dividing by *max_val*."""
    if max_val <= 0:
        return 0.0
    return min(scale, round((value / max_val) * scale, 1))


def _log_normalize(value: float, scale: float = 100.0) -> float:
    """Log-normalize a positive value to the 0-*scale* range."""
    if value <= 0:
        return 0.0
    return min(scale, round(math.log10(value) / math.log10(100000) * scale, 1))


def _days_since(iso_str: str | None) -> float:
    """Return number of days since the given ISO datetime string."""
    if not iso_str:
        return float("inf")
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except (ValueError, TypeError):
        return float("inf")


def _compute_overall(scores: dict[str, float]) -> str:
    """Compute weighted overall score and return a letter grade."""
    overall = (
        scores.get("activity", 0) * W_ACTIVITY
        + scores.get("community", 0) * W_COMMUNITY
        + scores.get("documentation", 0) * W_DOCUMENTATION
        + scores.get("scale", 0) * W_SCALE
        + scores.get("stability", 0) * W_STABILITY
        + scores.get("impact", 0) * W_IMPACT
    )
    for threshold, grade in GRADE_THRESHOLDS:
        if overall >= threshold:
            return grade
    return "D"


# ── Dimension calculators ─────────────────────────────────────────────


def _calc_activity(data: dict) -> float:
    """
    Activity score (0-100).
    Factors: commit frequency from code_frequency weeks, days since last push.
    """
    weeks = data.get("commit_weeks", [])
    recent_commits = 0
    # Count commits in the last ~4 weeks (4 entries in code_frequency list)
    for week in weeks[-4:]:
        if isinstance(week, list) and len(week) >= 3:
            recent_commits += abs(week[1]) + abs(week[2])  # additions + deletions

    commit_score = _normalize(recent_commits, 5000)

    days_since_push = _days_since(data.get("pushed_at"))
    recency_score = 100.0
    if days_since_push > 90:
        recency_score = 10.0
    elif days_since_push > 30:
        recency_score = 40.0
    elif days_since_push > 7:
        recency_score = 70.0

    return round(commit_score * 0.6 + recency_score * 0.4, 1)


def _calc_community(data: dict) -> float:
    """
    Community score (0-100).
    Factors: issue closure rate, PR closure rate.
    """
    # GitHub API doesn't easily give closed counts without extra calls,
    # so we approximate using open_issues vs total.
    # A repo with many issues might be well-maintained (high engagement).
    # We'll use a heuristic based on open_issues count and repo size.
    open_issues = data.get("open_issues_count", 0)
    stars = data.get("stars", 0)

    # If there are very few open issues relative to stars, that's good.
    if stars > 0:
        issue_ratio = open_issues / max(stars, 1)
        if issue_ratio < 0.01:
            return 90.0
        elif issue_ratio < 0.05:
            return 75.0
        elif issue_ratio < 0.1:
            return 60.0
        elif issue_ratio < 0.5:
            return 40.0
        else:
            return 20.0

    return 50.0


def _calc_documentation(data: dict) -> float:
    """Documentation score (0-100) based on README, CONTRIBUTING, and License."""
    score = 0.0
    if data.get("has_readme"):
        score += 40.0
    if data.get("has_contributing"):
        score += 30.0
    if data.get("license"):
        score += 30.0
    return score


def _calc_scale(data: dict) -> float:
    """
    Scale score (0-100).
    Factors: number of languages, total repository size.
    """
    languages = data.get("languages", {})
    num_langs = len(languages)
    total_bytes = sum(languages.values())

    lang_score = _normalize(num_langs, 10, 50)
    size_score = _normalize(total_bytes, 50 * 1024 * 1024, 50)  # 50 MB max

    return round(lang_score + size_score, 1)


def _calc_stability(data: dict) -> float:
    """
    Stability score (0-100).
    Factors: number of tags, existence of releases.
    """
    tag_count = data.get("tags_count", 0)
    has_releases = data.get("has_releases", False)

    tag_score = _normalize(tag_count, 20, 60)
    release_score = 40.0 if has_releases else 0.0

    return round(tag_score + release_score, 1)


def _calc_impact(data: dict) -> float:
    """
    Impact score (0-100).
    Log-normalize stars, forks, and watchers.
    """
    stars = data.get("stars", 0)
    forks = data.get("forks", 0)
    watchers = data.get("watchers", 0)

    star_score = _log_normalize(stars, 50)
    fork_score = _log_normalize(forks, 25)
    watch_score = _log_normalize(watchers, 25)

    return round(star_score + fork_score + watch_score, 1)


# ── Public API ─────────────────────────────────────────────────────────


def calculate_health_scores(data: dict) -> dict:
    """
    Calculate six-dimensional health scores and return a dict with scores, overall_grade.
    """
    # Extract commit activity weeks
    commit_activity = data.get("commit_activity", {})
    data["commit_weeks"] = commit_activity.get("weeks", [])

    scores = {
        "activity": _calc_activity(data),
        "community": _calc_community(data),
        "documentation": _calc_documentation(data),
        "scale": _calc_scale(data),
        "stability": _calc_stability(data),
        "impact": _calc_impact(data),
    }

    overall = _compute_overall(scores)

    return {
        "scores": scores,
        "overall_grade": overall,
    }


async def recommend_similar_repos(
    languages: dict,
    topics: list[str],
    current_repo_full_name: str,
) -> list[dict]:
    """
    Find similar repositories based on primary language and topics.
    Returns top 5 recommendations sorted by stars, excluding the current repo.
    """
    # Determine primary language (most bytes)
    primary_language = max(languages, key=languages.get) if languages else ""

    # Build search query
    query_parts = []
    if primary_language:
        query_parts.append(f"language:{primary_language}")
    if topics:
        # Use the first 3 topics for better search results
        for topic in topics[:3]:
            query_parts.append(f"topic:{topic}")

    if not query_parts:
        # Fallback: just search for high-quality repos
        return []

    query = " ".join(query_parts)
    results = await search_repos(query, sort="stars", per_page=10)

    # Filter out the current repo and take top 5
    recommendations = [
        r for r in results if r["full_name"] != current_repo_full_name
    ][:5]

    return recommendations


def compute_community_metrics(data: dict) -> dict:
    """Compute additional community metrics for the output."""
    return {
        "open_issues": data.get("open_issues_count", 0),
        "contributors_count": len(data.get("contributors", [])),
        "top_contributors": [
            c.get("login") for c in data.get("contributors", [])[:5]
        ],
        "tags_count": data.get("tags_count", 0),
        "has_releases": data.get("has_releases", False),
        "default_branch": data.get("default_branch", "main"),
        "total_size_kb": data.get("size", 0),
    }
