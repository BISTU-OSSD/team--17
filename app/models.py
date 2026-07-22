"""
DevSkillMapper - 结构化数据模型

所有模型均使用 Pydantic v2，输出给算法模块的原始数据遵循此 Schema。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── 仓库基本信息 ──────────────────────────────────────────

class RepoInfo(BaseModel):
    """仓库基本信息"""
    full_name: str = Field(..., description="仓库全名，例如 facebook/react")
    owner: str = Field(..., description="所有者")
    name: str = Field(..., description="仓库名")
    description: Optional[str] = Field(None, description="仓库描述")
    homepage: Optional[str] = Field(None, description="项目主页")
    language: Optional[str] = Field(None, description="主语言")
    topics: list[str] = Field(default_factory=list, description="话题标签")
    license: Optional[str] = Field(None, description="许可证 SPDX 标识")
    default_branch: str = Field("main", description="默认分支")

    # 指标
    stars: int = Field(0, description="Star 数")
    forks: int = Field(0, description="Fork 数")
    watchers: int = Field(0, description="Watcher 数")
    open_issues_count: int = Field(0, description="开放 Issue 数")
    size_kb: int = Field(0, description="仓库大小 (KB)")

    # 时间
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="最后更新时间")
    pushed_at: Optional[datetime] = Field(None, description="最后推送时间")

    archived: bool = Field(False, description="是否已归档")
    fork: bool = Field(False, description="是否为 Fork")


# ── 语言分布 ──────────────────────────────────────────────

class LanguageItem(BaseModel):
    """单项语言统计"""
    language: str = Field(..., description="语言名称")
    bytes: int = Field(0, description="字节数")
    percentage: float = Field(0.0, description="占比 (%)")


class LanguageStats(BaseModel):
    """语言分布汇总"""
    total_bytes: int = Field(0, description="总字节数")
    languages: list[LanguageItem] = Field(default_factory=list, description="各语言明细")


# ── Commit 活跃度 ─────────────────────────────────────────

class DailyCommit(BaseModel):
    """单日 Commit 统计"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    count: int = Field(0, description="当日提交数")


class CommitStats(BaseModel):
    """Commit 活跃度汇总"""
    total_commits_all_time: int = Field(0, description="历史总提交数（近似）")
    commits_last_30_days: int = Field(0, description="近 30 天提交数")
    commits_last_90_days: int = Field(0, description="近 90 天提交数")
    daily_commits: list[DailyCommit] = Field(default_factory=list, description="近 30 天每日提交分布")
    last_commit_date: Optional[str] = Field(None, description="最近一次提交日期")
    commit_frequency_per_week: float = Field(0.0, description="近 30 天平均每周提交次数")


# ── Issue 统计 ────────────────────────────────────────────

class IssueStats(BaseModel):
    """Issue 处理统计"""
    total_open: int = Field(0, description="当前开放 Issue 数")
    total_closed: int = Field(0, description="历史关闭 Issue 数")
    close_rate: float = Field(0.0, description="关闭率 (0-1)")
    avg_close_time_hours: Optional[float] = Field(None, description="平均关闭时长（小时）")
    recent_30d_opened: int = Field(0, description="近 30 天新建")
    recent_30d_closed: int = Field(0, description="近 30 天关闭")
    has_contributing_guide: bool = Field(False, description="是否有 CONTRIBUTING 文件")


# ── PR 统计 ───────────────────────────────────────────────

class PRStats(BaseModel):
    """Pull Request 统计"""
    total_open: int = Field(0, description="当前开放 PR 数")
    total_closed: int = Field(0, description="历史关闭 PR 数")
    total_merged: int = Field(0, description="已合并 PR 数")
    merge_rate: float = Field(0.0, description="合并率 (merged / closed)")
    avg_merge_time_hours: Optional[float] = Field(None, description="平均合并时长（小时）")
    recent_30d_opened: int = Field(0, description="近 30 天新建")
    recent_30d_merged: int = Field(0, description="近 30 天合并")


# ── 贡献者画像 ────────────────────────────────────────────

class ContributorItem(BaseModel):
    """单个贡献者"""
    login: str = Field(..., description="用户名")
    contributions: int = Field(0, description="贡献次数")
    avatar_url: str = Field("", description="头像地址")


class ContributorStats(BaseModel):
    """贡献者画像"""
    total_contributors: int = Field(0, description="全部贡献者数")
    active_30d_contributors: int = Field(0, description="近 30 天活跃贡献者数")
    top_contributors: list[ContributorItem] = Field(default_factory=list, description="Top 贡献者")
    new_contributor_ratio: float = Field(0.0, description="新贡献者占比（近 90 天）")
    bus_factor: int = Field(0, description="贡献集中度：贡献前 N 人占比 50%")


# ── 文档质量 ──────────────────────────────────────────────

class DocStats(BaseModel):
    """文档质量检测"""
    has_readme: bool = Field(False)
    readme_length: int = Field(0, description="README 字符数")
    has_license: bool = Field(False)
    license_spdx: Optional[str] = Field(None)
    has_contributing: bool = Field(False)
    has_code_of_conduct: bool = Field(False)
    has_changelog: bool = Field(False)


# ── 发布与版本 ────────────────────────────────────────────

class ReleaseStats(BaseModel):
    """发布与版本统计"""
    total_releases: int = Field(0)
    latest_release_tag: Optional[str] = Field(None)
    latest_release_date: Optional[str] = Field(None)
    release_frequency_6m: float = Field(0.0, description="近 6 月平均月发布数")


# ── 汇总报告（给算法模块的最终输出）──────────────────────

class RepoReport(BaseModel):
    """仓库完整体检原始数据 —— 算法模块的输入"""
    repo: RepoInfo = Field(..., description="仓库基本信息")
    languages: LanguageStats = Field(default_factory=LanguageStats, description="语言分布")
    commits: CommitStats = Field(default_factory=CommitStats, description="Commit 活跃度")
    issues: IssueStats = Field(default_factory=IssueStats, description="Issue 处理")
    pulls: PRStats = Field(default_factory=PRStats, description="PR 处理")
    contributors: ContributorStats = Field(default_factory=ContributorStats, description="贡献者画像")
    docs: DocStats = Field(default_factory=DocStats, description="文档质量")
    releases: ReleaseStats = Field(default_factory=ReleaseStats, description="发布与版本")

    # 元信息
    fetched_at: str = Field("", description="数据拉取时间 ISO 8601")
    from_cache: bool = Field(False, description="是否来自缓存")
