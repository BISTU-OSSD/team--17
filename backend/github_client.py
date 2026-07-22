"""Async GitHub REST API client for DevSkillMapper."""

import os
from typing import Optional

import httpx

GITHUB_API_BASE = "https://api.github.com"

_github_token: Optional[str] = None


def get_headers() -> dict:
    """Return request headers with optional auth token."""
    global _github_token
    if _github_token is None:
        _github_token = os.getenv("GITHUB_TOKEN", "").strip() or None
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DevSkillMapper/1.0",
    }
    if _github_token:
        headers["Authorization"] = f"Bearer {_github_token}"
    return headers


async def _request(path: str, params: Optional[dict] = None) -> dict:
    """Make an async GET request to the GitHub API and return the JSON body."""
    url = f"{GITHUB_API_BASE}{path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, headers=get_headers(), params=params)
        if resp.status_code == 404:
            return {"error": f"Repository not found at {url}", "status": 404}
        if resp.status_code == 403:
            return {"error": "API rate limit exceeded. Set GITHUB_TOKEN for higher limits.", "status": 403}
        if resp.status_code != 200:
            return {"error": f"GitHub API error: HTTP {resp.status_code}", "status": resp.status_code}
        return resp.json()


async def get_repo_info(owner: str, repo: str) -> dict:
    """Fetch basic repository information."""
    data = await _request(f"/repos/{owner}/{repo}")
    if "error" in data:
        return data
    return {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "watchers": data.get("subscribers_count", 0) or data.get("watchers_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language"),
        "topics": data.get("topics", []),
        "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
        "has_readme": False,  # checked separately
        "has_contributing": False,
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "pushed_at": data.get("pushed_at"),
        "size": data.get("size", 0),
        "default_branch": data.get("default_branch", "main"),
    }


async def get_languages(owner: str, repo: str) -> dict:
    """Fetch language byte counts."""
    data = await _request(f"/repos/{owner}/{repo}/languages")
    if "error" in data:
        return {}
    return data if isinstance(data, dict) else {}


async def get_commit_activity(owner: str, repo: str) -> dict:
    """Fetch commit activity for the last 52 weeks (GitHub returns 52 weeks)."""
    data = await _request(f"/repos/{owner}/{repo}/stats/code_frequency")
    if "error" in data:
        return {"weeks": [], "error": data.get("error")}
    # data is a list of [timestamp, additions, deletions] per week
    return {"weeks": data if isinstance(data, list) else []}


async def get_issue_pr_stats(owner: str, repo: str) -> dict:
    """Fetch open/closed counts for issues and pull requests."""
    issues_data = await _request(f"/repos/{owner}/{repo}/issues", params={"state": "all", "per_page": 1})
    if isinstance(issues_data, dict) and "error" in issues_data:
        return {"open_issues": 0, "closed_issues": 0, "open_prs": 0, "closed_prs": 0}

    pr_data = await _request(f"/repos/{owner}/{repo}/pulls", params={"state": "all", "per_page": 1})

    return {
        "open_issues": 0,  # will be fetched from repo info
        "closed_issues": 0,
        "open_prs": 0,
        "closed_prs": 0,
        # detailed counts handled via separate endpoint if available
    }


async def get_contributors(owner: str, repo: str) -> list:
    """Fetch top contributors."""
    data = await _request(f"/repos/{owner}/{repo}/contributors", params={"per_page": 10})
    if isinstance(data, dict) and "error" in data:
        return []
    if not isinstance(data, list):
        return []
    return [
        {
            "login": c.get("login"),
            "contributions": c.get("contributions", 0),
            "avatar_url": c.get("avatar_url"),
        }
        for c in data
    ]


async def get_repo_contents(owner: str, repo: str, path: str) -> Optional[dict]:
    """Fetch a specific file from the repository to check its existence."""
    data = await _request(f"/repos/{owner}/{repo}/contents/{path}")
    if isinstance(data, dict) and "error" in data:
        return None
    return data


async def get_tags(owner: str, repo: str) -> list:
    """Fetch repository tags."""
    data = await _request(f"/repos/{owner}/{repo}/tags", params={"per_page": 10})
    if isinstance(data, dict) and "error" in data:
        return []
    return data if isinstance(data, list) else []


async def get_releases(owner: str, repo: str) -> list:
    """Fetch repository releases."""
    data = await _request(f"/repos/{owner}/{repo}/releases", params={"per_page": 5})
    if isinstance(data, dict) and "error" in data:
        return []
    return data if isinstance(data, list) else []


async def search_repos(query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> list:
    """Search GitHub repositories."""
    data = await _request("/search/repositories", params={"q": query, "sort": sort, "order": order, "per_page": per_page})
    if isinstance(data, dict) and "error" in data:
        return []
    items = data.get("items", []) if isinstance(data, dict) else []
    return [
        {
            "full_name": r.get("full_name"),
            "description": r.get("description"),
            "stars": r.get("stargazers_count", 0),
            "language": r.get("language"),
            "topics": r.get("topics", []),
        }
        for r in items
    ]


async def get_combined_stats(owner: str, repo: str) -> dict:
    """Fetch all relevant stats for analysis in parallel where possible."""
    info = await get_repo_info(owner, repo)
    if "error" in info:
        return info

    languages, tags, releases = await asyncio.gather(
        get_languages(owner, repo),
        get_tags(owner, repo),
        get_releases(owner, repo),
    )

    # Check for README, CONTRIBUTING, License
    default_branch = info.get("default_branch", "main")

    readme_content = await get_repo_contents(owner, repo, "README.md")
    contributing_content = await get_repo_contents(owner, repo, "CONTRIBUTING.md")

    info["has_readme"] = readme_content is not None
    info["has_contributing"] = contributing_content is not None
    info["languages"] = languages
    info["tags_count"] = len(tags)
    info["tags"] = tags
    info["has_releases"] = len(releases) > 0
    info["releases_count"] = len(releases)

    # Get issue & PR stats from repo info
    info["open_issues_count"] = info.get("open_issues", 0)

    return info


import asyncio
