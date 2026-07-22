"""
DevSkillMapper - GitHub API 客户端

封装 GitHub REST API 的数据获取逻辑，包含：
  - 异步请求（httpx）
  - 限流感知（X-RateLimit-* 头）
  - 异常处理（限流 / 仓库不存在 / 认证失败）
  - 自动分页（Link 头遍历）
  - 缓存集成（内存 + SQLite）
  - 条件请求（ETag / If-None-Match）以减少 API 消耗
"""
from __future__ import annotations

import asyncio
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from .cache import cache
from .config import (
    GITHUB_API_BASE,
    GITHUB_TOKEN,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
    DEFAULT_PER_PAGE,
    VERIFY_SSL,
)
from .models import (
    RepoInfo,
    LanguageItem,
    LanguageStats,
    DailyCommit,
    CommitStats,
    IssueStats,
    PRStats,
    ContributorItem,
    ContributorStats,
    DocStats,
    ReleaseStats,
    RepoReport,
)


# ── 自定义异常 ───────────────────────────────────────────

class GitHubAPIError(Exception):
    """GitHub API 调用基础异常"""
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.status_code = status_code


class RepoNotFoundError(GitHubAPIError):
    """仓库不存在 (404)"""


class RateLimitExceededError(GitHubAPIError):
    """API 限流 (403 / 429)，携带 reset 时间戳"""
    def __init__(self, message: str, reset_at: Optional[datetime] = None) -> None:
        super().__init__(message, status_code=429)
        self.reset_at = reset_at


class AuthenticationError(GitHubAPIError):
    """Token 无效或权限不足 (401)"""


# ── 工具函数 ─────────────────────────────────────────────

_PAGE_RE = re.compile(r'<([^>]+)>;\s*rel="(\w+)"')


def _parse_link_header(link: str) -> dict[str, str]:
    """解析 Link 头，返回 {'next': url, 'last': url, ...}"""
    links: dict[str, str] = {}
    for part in link.split(","):
        m = _PAGE_RE.search(part)
        if m:
            links[m.group(2)] = m.group(1)
    return links


def _extract_owner_repo(input_str: str) -> tuple[str, str]:
    """
    从多种输入格式提取 owner/repo：
      - facebook/react
      - https://github.com/facebook/react
      - https://github.com/facebook/react.git
    """
    cleaned = input_str.rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    # 全 URL 形式
    if cleaned.startswith("https://github.com/"):
        parts = cleaned[len("https://github.com/"):].split("/")
    elif cleaned.startswith("http://github.com/"):
        parts = cleaned[len("http://github.com/"):].split("/")
    else:
        parts = cleaned.split("/")
    if len(parts) < 2:
        raise ValueError(f"无法解析仓库路径: {input_str}")
    return parts[0], parts[1]


# ── GitHub API 客户端 ────────────────────────────────────

class GitHubClient:
    """GitHub REST API 异步客户端"""

    def __init__(self, token: str = "") -> None:
        self._token = token or GITHUB_TOKEN
        self._client: Optional[httpx.AsyncClient] = None
        # 限流状态追踪
        self._rate_remaining = 0
        self._rate_reset: Optional[datetime] = None
        # ETag 条件请求缓存（减少 API 消耗）
        self._etags: dict[str, str] = {}

    # ── 生命周期 ────────────────────────────────────────

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {
                "Accept": "application/vnd.github+json",
                "User-Agent": "DevSkillMapper/1.0",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

            self._client = httpx.AsyncClient(
                base_url=GITHUB_API_BASE,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                verify=VERIFY_SSL,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ── 核心请求方法 ────────────────────────────────────

    async def _request(
        self, method: str, path: str, params: dict | None = None,
        use_etag: bool = False,
    ) -> httpx.Response:
        """
        发送请求，自动重试、处理限流。
        返回响应对象，调用方负责解析。
        """
        client = await self._ensure_client()
        url = path  # httpx 的 base_url + path 自动拼接

        headers: dict[str, str] = {}
        if use_etag and path in self._etags:
            headers["If-None-Match"] = self._etags[path]

        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            resp = await client.request(method, url, params=params, headers=headers)

            # 更新限流状态
            self._rate_remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
            reset_epoch = int(resp.headers.get("X-RateLimit-Reset", 0))
            if reset_epoch:
                self._rate_reset = datetime.fromtimestamp(reset_epoch, tz=timezone.utc)

            # 保存 ETag
            if "ETag" in resp.headers:
                self._etags[path] = resp.headers["ETag"]

            # 304 Not Modified（条件请求命中，数据未变）
            if resp.status_code == 304:
                return resp  # 调用方需自行 fallback

            # 403 限流
            if resp.status_code == 403 and self._rate_remaining == 0:
                reset_at = self._rate_reset
                raise RateLimitExceededError(
                    f"API 限流已达上限，重置时间: {reset_at}",
                    reset_at=reset_at,
                )

            # 429 次级限流
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = int(retry_after) if retry_after else 60
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(wait)
                    continue
                raise RateLimitExceededError("API 次级限流 (429)")

            # 404
            if resp.status_code == 404:
                raise RepoNotFoundError("仓库不存在或为私有仓库", status_code=404)

            # 401
            if resp.status_code == 401:
                raise AuthenticationError("Token 无效或未提供", status_code=401)

            # 2xx 成功
            if resp.is_success:
                return resp

            # 其他错误 → 重试
            last_exc = GitHubAPIError(
                f"GitHub API 返回 {resp.status_code}: {resp.text[:200]}",
                status_code=resp.status_code,
            )
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF ** attempt
                await asyncio.sleep(wait)
            else:
                raise last_exc

        raise last_exc  # type: ignore[misc]

    async def _get(self, path: str, params: dict | None = None, use_etag: bool = False) -> httpx.Response:
        return await self._request("GET", path, params=params, use_etag=use_etag)

    async def _get_json(self, path: str, params: dict | None = None) -> Any:
        """GET 并自动解析 JSON，支持缓存"""
        cache_key = cache.make_key(path, "json")
        cached = await cache.get(cache_key)
        if cached is not None:
            return cached
        resp = await self._get(path, params=params)
        data = resp.json()
        await cache.set(cache_key, data)
        return data

    async def _paginate(self, path: str, params: dict | None = None, max_pages: int = 5) -> list[dict]:
        """
        自动翻页获取全量数据（最多 max_pages 页）。
        返回合并后的 JSON 列表。
        """
        all_data: list[dict] = []
        next_url = path
        base_params = dict(params or {})
        page_count = 0

        while next_url and page_count < max_pages:
            # 如果是完整 URL（Link 头返回的），提取 path
            if next_url.startswith(GITHUB_API_BASE):
                next_url = next_url[len(GITHUB_API_BASE):]

            resp = await self._get(next_url, params=base_params)
            data: list[dict] = resp.json()
            if not isinstance(data, list):
                break
            all_data.extend(data)

            # 检查 Link 头获取下一页
            link_header = resp.headers.get("Link", "")
            links = _parse_link_header(link_header)
            next_url = links.get("next", "")
            base_params = {}  # Link 中的 URL 已包含参数
            page_count += 1

        return all_data

    # ── 仓库校验 ────────────────────────────────────────

    @staticmethod
    def validate_input(input_str: str) -> str:
        """校验并标准化仓库输入，返回 "owner/repo" 格式"""
        if not input_str or not input_str.strip():
            raise ValueError("仓库路径不能为空")
        owner, repo = _extract_owner_repo(input_str.strip())
        return f"{owner}/{repo}"

    # ── 数据获取方法 ────────────────────────────────────

    async def get_repo_info(self, full_name: str) -> RepoInfo:
        """获取仓库基本信息"""
        owner, repo = full_name.split("/")
        data = await self._get_json(f"/repos/{owner}/{repo}")

        license_spdx: Optional[str] = None
        lic = data.get("license")
        if lic and isinstance(lic, dict):
            license_spdx = lic.get("spdx_id")

        topics: list[str] = data.get("topics", [])

        return RepoInfo(
            full_name=data.get("full_name", full_name),
            owner=data.get("owner", {}).get("login", owner),
            name=data.get("name", repo),
            description=data.get("description"),
            homepage=data.get("homepage"),
            language=data.get("language"),
            topics=topics,
            license=license_spdx,
            default_branch=data.get("default_branch", "main"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            size_kb=data.get("size", 0),
            created_at=_parse_dt(data.get("created_at")),
            updated_at=_parse_dt(data.get("updated_at")),
            pushed_at=_parse_dt(data.get("pushed_at")),
            archived=data.get("archived", False),
            fork=data.get("fork", False),
        )

    async def get_languages(self, full_name: str) -> LanguageStats:
        """获取语言分布"""
        owner, repo = full_name.split("/")
        data = await self._get_json(f"/repos/{owner}/{repo}/languages")
        # data 格式: {"Python": 12345, "JavaScript": 6789, ...}
        total = sum(data.values())
        items: list[LanguageItem] = []
        for lang, byte_count in sorted(data.items(), key=lambda x: -x[1]):
            pct = (byte_count / total * 100) if total > 0 else 0
            items.append(LanguageItem(language=lang, bytes=byte_count, percentage=round(pct, 1)))
        return LanguageStats(total_bytes=total, languages=items)

    async def get_commit_stats(self, full_name: str) -> CommitStats:
        """获取 Commit 活跃度统计"""
        owner, repo = full_name.split("/")
        since_90d = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()

        # 近 90 天 commit（最多 3 页，约 90 条）
        commits_90d = await self._paginate(
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": DEFAULT_PER_PAGE, "since": since_90d},
            max_pages=3,
        )

        # 过滤近 30 天
        cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
        commits_30d = [
            c for c in commits_90d
            if _parse_dt(c["commit"]["author"]["date"]) and _parse_dt(c["commit"]["author"]["date"]) >= cutoff_30d  # type: ignore[operator]
        ]

        # 每日分布
        day_map: dict[str, int] = {}
        for c in commits_30d:
            dt = _parse_dt(c["commit"]["author"]["date"])
            if dt:
                day = dt.strftime("%Y-%m-%d")
                day_map[day] = day_map.get(day, 0) + 1
        daily = [
            DailyCommit(date=d, count=c)
            for d, c in sorted(day_map.items())
        ]

        total_30d = sum(d.count for d in daily)
        total_90d = len(commits_90d)

        # 总提交数（近似）：用 commit 列表的长度估算
        # 更精确的需要额外请求，这里用 90 天数据 + 贡献者 sum 近似
        last_date = daily[-1].date if daily else None

        return CommitStats(
            total_commits_all_time=0,  # 需额外请求获取
            commits_last_30_days=total_30d,
            commits_last_90_days=total_90d,
            daily_commits=daily,
            last_commit_date=last_date,
            commit_frequency_per_week=round(total_30d / 4.29, 1) if total_30d > 0 else 0.0,
        )

    async def get_issue_stats(self, full_name: str) -> IssueStats:
        """获取 Issue 处理统计"""
        owner, repo = full_name.split("/")

        # 开放 Issues
        open_resp = await self._get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": "open", "per_page": 1, "filter": "all"},
        )
        # 从 Link 头获取总数（GitHub 只在最后一页有 link）
        # 简单方案：用仓库基础信息中的 open_issues_count
        # 更准确方案：分页统计最近关闭的
        total_open_str = ""
        if "Link" in open_resp.headers:
            links = _parse_link_header(open_resp.headers["Link"])
            last_url = links.get("last", "")
            if "page=" in last_url:
                # 提取 page= 参数
                import re as _re
                m = _re.search(r"[?&]page=(\d+)", last_url)
                if m:
                    total_open_str = m.group(1)

        open_list = open_resp.json()
        total_open = int(total_open_str) if total_open_str else len(open_list)

        # 最近关闭的 Issues（近 90 天）
        since_90d = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        closed_issues = await self._paginate(
            f"/repos/{owner}/{repo}/issues",
            params={"state": "closed", "per_page": DEFAULT_PER_PAGE, "since": since_90d, "filter": "all"},
            max_pages=3,
        )

        # 过滤掉 PR（GitHub Issues API 返回 PR 也混在里面）
        pure_issues = [i for i in closed_issues if "pull_request" not in i]

        # 关闭率（用近 90 天数据估算）
        total_closed = len(pure_issues)
        since_30d = datetime.now(timezone.utc) - timedelta(days=30)
        recent_opened = len([i for i in pure_issues if _parse_dt(i.get("created_at")) and _parse_dt(i.get("created_at")) >= since_30d])  # type: ignore[operator]
        recent_closed = len([i for i in pure_issues if _parse_dt(i.get("closed_at")) and _parse_dt(i.get("closed_at")) >= since_30d])  # type: ignore[operator]

        # 平均关闭时长
        durations: list[float] = []
        for i in pure_issues:
            created = _parse_dt(i.get("created_at"))
            closed = _parse_dt(i.get("closed_at"))
            if created and closed:
                durations.append((closed - created).total_seconds() / 3600)
        avg_hours = round(sum(durations) / len(durations), 1) if durations else None

        # 关闭率（整体估算）
        if total_open + total_closed > 0:
            close_rate = round(total_closed / (total_open + total_closed), 3)
        else:
            close_rate = 0.0

        # CONTRIBUTING 检查
        has_contrib = await self._check_file(full_name, "CONTRIBUTING.md")

        return IssueStats(
            total_open=total_open,
            total_closed=total_closed,
            close_rate=close_rate,
            avg_close_time_hours=avg_hours,
            recent_30d_opened=recent_opened,
            recent_30d_closed=recent_closed,
            has_contributing_guide=has_contrib,
        )

    async def get_pr_stats(self, full_name: str) -> PRStats:
        """获取 PR 统计"""
        owner, repo = full_name.split("/")

        async def _count_prs(state: str) -> tuple[int, list[dict]]:
            """统计某状态的 PR 数量并返回列表"""
            items = await self._paginate(
                f"/repos/{owner}/{repo}/pulls",
                params={"state": state, "per_page": DEFAULT_PER_PAGE},
                max_pages=3,
            )
            return len(items), items

        open_count, open_list = await _count_prs("open")
        closed_count, closed_list = await _count_prs("closed")

        # 已合并 PR（GitHub 把 merged 视为 closed 的子集）
        merged_list = [p for p in closed_list if p.get("merged_at")]
        merged_count = len(merged_list)

        merge_rate = round(merged_count / closed_count, 3) if closed_count > 0 else 0.0

        # 平均合并时长
        durations: list[float] = []
        for p in merged_list:
            created = _parse_dt(p.get("created_at"))
            merged = _parse_dt(p.get("merged_at"))
            if created and merged:
                durations.append((merged - created).total_seconds() / 3600)
        avg_merge_hours = round(sum(durations) / len(durations), 1) if durations else None

        # 近 30 天
        since_30d = datetime.now(timezone.utc) - timedelta(days=30)
        recent_opened = sum(1 for p in open_list + closed_list if _parse_dt(p.get("created_at")) and _parse_dt(p.get("created_at")) >= since_30d)  # type: ignore[operator]
        recent_merged = sum(1 for p in merged_list if _parse_dt(p.get("merged_at")) and _parse_dt(p.get("merged_at")) >= since_30d)  # type: ignore[operator]

        return PRStats(
            total_open=open_count,
            total_closed=closed_count,
            total_merged=merged_count,
            merge_rate=merge_rate,
            avg_merge_time_hours=avg_merge_hours,
            recent_30d_opened=recent_opened,
            recent_30d_merged=recent_merged,
        )

    async def get_contributor_stats(self, full_name: str) -> ContributorStats:
        """获取贡献者画像"""
        owner, repo = full_name.split("/")

        contributors = await self._paginate(
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": DEFAULT_PER_PAGE},
            max_pages=2,
        )

        top_items = [
            ContributorItem(
                login=c["login"],
                contributions=c.get("contributions", 0),
                avatar_url=c.get("avatar_url", ""),
            )
            for c in contributors[:10]
        ]

        total = len(contributors)

        # 近 30 天活跃贡献者（通过 commit 作者统计）
        since_30d = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        commits_30d = await self._paginate(
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": DEFAULT_PER_PAGE, "since": since_30d},
            max_pages=3,
        )
        active_authors = set()
        for c in commits_30d:
            author = c.get("author")
            if author and author.get("login"):
                active_authors.add(author["login"])
            elif c.get("commit", {}).get("author", {}).get("name"):
                # fallback: 某些 commit 没有 GitHub 登录名
                active_authors.add(c["commit"]["author"]["name"])

        active_count = len(active_authors)

        # 新贡献者占比（近 90 天首次贡献）
        since_90d = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        commits_90d = await self._paginate(
            f"/repos/{owner}/{repo}/commits",
            params={"per_page": DEFAULT_PER_PAGE, "since": since_90d},
            max_pages=3,
        )
        authors_90d = set()
        for c in commits_90d:
            author = c.get("author")
            if author and author.get("login"):
                authors_90d.add(author["login"])
            elif c.get("commit", {}).get("author", {}).get("name"):
                authors_90d.add(c["commit"]["author"]["name"])

        # 新贡献者 = 近 90 天出现但不在这 90 天前贡献的人
        # 简化处理：用 active 与 90d 的比值
        new_ratio = round(active_count / max(len(authors_90d), 1), 3) if authors_90d else 0.0

        # Bus Factor：前 N 人贡献占比超过 50% 的 N
        all_contribs = sorted([c.get("contributions", 0) for c in contributors], reverse=True)
        total_con = sum(all_contribs)
        cum = 0
        bus = 0
        for con in all_contribs:
            cum += con
            bus += 1
            if cum >= total_con * 0.5:
                break

        return ContributorStats(
            total_contributors=total,
            active_30d_contributors=active_count,
            top_contributors=top_items,
            new_contributor_ratio=new_ratio,
            bus_factor=bus,
        )

    async def get_doc_stats(self, full_name: str) -> DocStats:
        """检测文档质量"""
        owner, repo = full_name.split("/")

        # 并行检查各文件
        files_to_check = [
            ("readme", "README.md"),
            ("contributing", "CONTRIBUTING.md"),
            ("code_of_conduct", "CODE_OF_CONDUCT.md"),
            ("changelog", "CHANGELOG.md"),
        ]

        results: dict[str, tuple[bool, int]] = {}
        for _, filename in files_to_check:
            exists, length = await self._check_file_with_length(full_name, filename)
            results[filename] = (exists, length)

        readme_exists, readme_len = results["README.md"]

        # License
        has_license = False
        license_spdx: Optional[str] = None
        try:
            lic_data = await self._get_json(f"/repos/{owner}/{repo}/license")
            has_license = True
            license_spdx = lic_data.get("license", {}).get("spdx_id")
        except (GitHubAPIError, Exception):
            pass

        return DocStats(
            has_readme=readme_exists,
            readme_length=readme_len,
            has_license=has_license,
            license_spdx=license_spdx,
            has_contributing=results["CONTRIBUTING.md"][0],
            has_code_of_conduct=results["CODE_OF_CONDUCT.md"][0],
            has_changelog=results["CHANGELOG.md"][0],
        )

    async def get_release_stats(self, full_name: str) -> ReleaseStats:
        """获取发布版本统计"""
        owner, repo = full_name.split("/")

        releases = await self._paginate(
            f"/repos/{owner}/{repo}/releases",
            params={"per_page": DEFAULT_PER_PAGE},
            max_pages=2,
        )

        if not releases:
            return ReleaseStats()

        latest = releases[0]
        total = len(releases)

        # 近 6 月发布频率
        cutoff_6m = datetime.now(timezone.utc) - timedelta(days=180)
        recent_count = sum(
            1 for r in releases
            if _parse_dt(r.get("published_at")) and _parse_dt(r.get("published_at")) >= cutoff_6m  # type: ignore[operator]
        )
        freq_6m = round(recent_count / 6.0, 1)

        return ReleaseStats(
            total_releases=total,
            latest_release_tag=latest.get("tag_name"),
            latest_release_date=_dt_str(latest.get("published_at")),
            release_frequency_6m=freq_6m,
        )

    # ── 文件检查辅助 ────────────────────────────────────

    async def _check_file(self, full_name: str, filename: str) -> bool:
        """检查仓库是否存在某文件（HEAD 请求）"""
        owner, repo = full_name.split("/")
        try:
            client = await self._ensure_client()
            resp = await client.head(
                f"/repos/{owner}/{repo}/contents/{filename}",
                headers={"Accept": "application/vnd.github+json"},
            )
            return resp.status_code == 200
        except Exception:
            return False

    async def _check_file_with_length(self, full_name: str, filename: str) -> tuple[bool, int]:
        """检查文件是否存在并返回内容长度"""
        owner, repo = full_name.split("/")
        try:
            client = await self._ensure_client()
            resp = await client.get(
                f"/repos/{owner}/{repo}/contents/{filename}",
                headers={"Accept": "application/vnd.github.raw"},
            )
            if resp.status_code == 200:
                content = resp.text
                return True, len(content)
            return False, 0
        except Exception:
            return False, 0

    # ── 综合报告 ────────────────────────────────────────

    async def get_full_report(self, full_name: str, force_refresh: bool = False) -> RepoReport:
        """
        获取仓库完整体检原始数据。
        整合所有数据源，是算法模块的直接输入。

        Args:
            full_name: 仓库全名，如 "facebook/react"
            force_refresh: 是否强制刷新缓存

        Returns:
            RepoReport 结构化原始数据
        """
        # 检查综合缓存
        report_cache_key = cache.make_key(full_name, "full_report")
        if not force_refresh:
            cached_report = await cache.get(report_cache_key)
            if cached_report is not None:
                # 反序列化 Pydantic
                return RepoReport.model_validate(cached_report)

        # 并行获取所有数据（注：部分接口互不依赖可并发）
        repo_info, languages, doc_stats, release_stats = await asyncio.gather(
            self.get_repo_info(full_name),
            self.get_languages(full_name),
            self.get_doc_stats(full_name),
            self.get_release_stats(full_name),
        )

        commits, issues, pulls, contributors = await asyncio.gather(
            self.get_commit_stats(full_name),
            self.get_issue_stats(full_name),
            self.get_pr_stats(full_name),
            self.get_contributor_stats(full_name),
        )

        report = RepoReport(
            repo=repo_info,
            languages=languages,
            commits=commits,
            issues=issues,
            pulls=pulls,
            contributors=contributors,
            docs=doc_stats,
            releases=release_stats,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            from_cache=False,
        )

        # 写入综合缓存
        await cache.set(report_cache_key, report.model_dump(), ttl=600)

        return report

    # ── 限流信息（供前端展示） ────────────────────────────

    @property
    def rate_limit_info(self) -> dict:
        return {
            "remaining": self._rate_remaining,
            "reset_at": self._rate_reset.isoformat() if self._rate_reset else None,
            "has_token": bool(self._token),
        }


# ── 时间工具 ─────────────────────────────────────────────

def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """解析 ISO 8601 时间字符串"""
    if not value:
        return None
    try:
        # Python 3.11+ 支持 Z 后缀，这里手动兼容
        s = value.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _dt_str(value: Optional[str]) -> Optional[str]:
    """返回日期字符串 YYYY-MM-DD"""
    if not value:
        return None
    try:
        return value[:10]
    except Exception:
        return None
