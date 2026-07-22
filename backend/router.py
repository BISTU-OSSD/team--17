"""API routes for DevSkillMapper."""

import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from analyzer import calculate_health_scores, recommend_similar_repos, compute_community_metrics
from github_client import get_combined_stats, get_commit_activity, get_contributors
from models import RepoRequest, RepoAnalysis, HealthScores

router = APIRouter()

# ── Simple in-memory cache ────────────────────────────────────────────
_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 3600  # 1 hour


def _get_cached(key: str):
    entry = _cache.get(key)
    if entry is None:
        return None
    ts, data = entry
    if time.time() - ts > CACHE_TTL:
        del _cache[key]
        return None
    return data


def _set_cache(key: str, data: dict):
    _cache[key] = (time.time(), data)


@router.post("/api/analyze", response_model=RepoAnalysis)
async def analyze_repo(req: RepoRequest):
    """Analyze a GitHub repository and return health scores, metrics, and recommendations."""
    repo_full_name = req.repo_full_name.strip()

    # Check cache
    cached = _get_cached(repo_full_name)
    if cached:
        return RepoAnalysis(**cached)

    # Parse owner/repo
    parts = repo_full_name.split("/")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid repository format. Use 'owner/repo'.")
    owner, repo = parts[0], parts[1]

    # Fetch GitHub data
    info = await get_combined_stats(owner, repo)
    if "error" in info:
        status = info.get("status", 500)
        if status == 404:
            raise HTTPException(status_code=404, detail=info["error"])
        elif status == 403:
            raise HTTPException(status_code=429, detail=info["error"])
        else:
            raise HTTPException(status_code=status, detail=info["error"])

    # Fetch commit activity and contributors
    commit_activity = await get_commit_activity(owner, repo)
    contributors = await get_contributors(owner, repo)

    # Merge data for analysis
    analysis_data = {**info}
    analysis_data["commit_activity"] = commit_activity
    analysis_data["contributors"] = contributors

    # Calculate health scores
    health_result = calculate_health_scores(analysis_data)
    scores = health_result["scores"]
    overall_grade = health_result["overall_grade"]

    # Compute additional metrics
    community_metrics = compute_community_metrics(analysis_data)

    # Recommend similar repos
    recommendations = await recommend_similar_repos(
        info.get("languages", {}),
        info.get("topics", []),
        repo_full_name,
    )

    result = {
        "full_name": info.get("full_name", repo_full_name),
        "description": info.get("description"),
        "stars": info.get("stars", 0),
        "forks": info.get("forks", 0),
        "watchers": info.get("watchers", 0),
        "open_issues": info.get("open_issues_count", 0),
        "language": info.get("language"),
        "languages": info.get("languages", {}),
        "topics": info.get("topics", []),
        "health_scores": HealthScores(**scores),
        "overall_grade": overall_grade,
        "community_metrics": community_metrics,
        "recommendations": recommendations,
        "license_name": info.get("license"),
        "has_readme": info.get("has_readme", False),
        "has_contributing": info.get("has_contributing", False),
    }

    # Cache and return
    _set_cache(repo_full_name, result)
    return RepoAnalysis(**result)
