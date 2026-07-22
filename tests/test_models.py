"""
测试 Pydantic 数据模型（纯单元测试）。
"""
from app.models import (
    RepoInfo,
    LanguageStats,
    LanguageItem,
    CommitStats,
    IssueStats,
    PRStats,
    ContributorStats,
    ContributorItem,
    DocStats,
    ReleaseStats,
    RepoReport,
)


def make_repo_info(**overrides) -> RepoInfo:
    """构造 RepoInfo 对象的工厂函数（owner/name 为必填字段）"""
    defaults = dict(
        full_name="facebook/react",
        owner="facebook",
        name="react",
        description="A JS library",
        html_url="https://github.com/facebook/react",
        stars=230000,
        forks=46000,
        watchers=6700,
        language="JavaScript",
        topics=["react", "ui"],
        license="MIT",
        default_branch="main",
        created_at="2013-05-24T00:00:00Z",
        updated_at="2026-07-01T00:00:00Z",
        pushed_at="2026-07-01T00:00:00Z",
        archived=False,
    )
    defaults.update(overrides)
    return RepoInfo(**defaults)


class TestRepoInfo:
    def test_basic(self):
        r = make_repo_info()
        assert r.full_name == "facebook/react"
        assert r.owner == "facebook"
        assert r.name == "react"
        assert r.stars == 230000
        assert "react" in r.topics
        assert r.archived is False

    def test_archived(self):
        r = make_repo_info(archived=True)
        assert r.archived is True

    def test_no_license(self):
        r = make_repo_info(license=None)
        assert r.license is None

    def test_no_description(self):
        r = make_repo_info(description=None)
        assert r.description is None

    def test_minimal_required_only(self):
        """只提供必填字段"""
        r = RepoInfo(full_name="x/y", owner="x", name="y")
        assert r.full_name == "x/y"
        assert r.stars == 0  # 默认值
        assert r.archived is False
        assert r.topics == []


class TestLanguageStats:
    def test_with_items(self):
        items = [
            LanguageItem(language="Python", bytes=80000, percentage=80.0),
            LanguageItem(language="JavaScript", bytes=20000, percentage=20.0),
        ]
        stats = LanguageStats(languages=items, total_bytes=100000)
        assert stats.total_bytes == 100000
        assert len(stats.languages) == 2
        assert stats.languages[0].language == "Python"
        assert sum(item.percentage for item in stats.languages) == 100.0

    def test_empty(self):
        stats = LanguageStats()
        assert stats.total_bytes == 0
        assert stats.languages == []


class TestCommitStats:
    def test_frequency(self):
        s = CommitStats(
            commits_last_30_days=15,
            commits_last_90_days=45,
            commit_frequency_per_week=5.0,
            last_commit_date="2026-07-20",
        )
        assert s.commits_last_30_days == 15
        assert s.commit_frequency_per_week == 5.0

    def test_default(self):
        s = CommitStats()
        assert s.commits_last_30_days == 0
        assert s.last_commit_date is None


class TestIssueStats:
    def test_rates(self):
        s = IssueStats(
            total_open=10,
            total_closed=90,
            close_rate=0.9,
            avg_close_time_hours=48.5,
        )
        assert s.close_rate == 0.9
        assert s.total_open + s.total_closed == 100


class TestPRStats:
    def test_merge_rate(self):
        s = PRStats(
            total_open=5,
            total_closed=95,
            total_merged=80,
            merge_rate=80.0 / 95,
        )
        assert s.total_merged == 80
        assert 0.8 < s.merge_rate < 0.9


class TestContributorStats:
    def test_top_contributors(self):
        items = [
            ContributorItem(login="alice", contributions=100, avatar_url="https://example.com/a.png"),
            ContributorItem(login="bob", contributions=50, avatar_url="https://example.com/b.png"),
        ]
        s = ContributorStats(
            total_contributors=20,
            active_30d_contributors=5,
            top_contributors=items,
            new_contributor_ratio=0.15,
            bus_factor=3,
        )
        assert s.total_contributors == 20
        assert s.top_contributors[0].login == "alice"
        assert s.bus_factor == 3
        assert s.new_contributor_ratio == 0.15


class TestDocStats:
    def test_full_docs(self):
        s = DocStats(
            has_readme=True,
            readme_length=5000,
            has_license=True,
            license_spdx="MIT",
            has_contributing=True,
        )
        assert s.has_readme is True
        assert s.readme_length == 5000
        assert s.license_spdx == "MIT"

    def test_minimal_docs(self):
        s = DocStats()
        assert s.has_readme is False
        assert s.license_spdx is None
        assert s.readme_length == 0


class TestReleaseStats:
    def test_with_releases(self):
        s = ReleaseStats(
            total_releases=5,
            latest_release_tag="v2.0.0",
            latest_release_date="2026-06-01",
            release_frequency_6m=2.0,
        )
        assert s.total_releases == 5
        assert s.latest_release_tag == "v2.0.0"
        assert s.release_frequency_6m == 2.0

    def test_no_releases(self):
        s = ReleaseStats()
        assert s.total_releases == 0
        assert s.latest_release_tag is None


class TestRepoReport:
    def test_full_report_structure(self):
        """测试 RepoReport 完整结构能正常构造"""
        r = make_repo_info()
        report = RepoReport(
            repo=r,
            fetched_at="2026-07-22T10:00:00",
            from_cache=False,
        )
        assert report.repo.full_name == "facebook/react"
        assert report.from_cache is False
        assert report.languages.total_bytes == 0  # 默认值
        assert report.commits.commits_last_30_days == 0  # 默认值
        assert report.fetched_at == "2026-07-22T10:00:00"

    def test_serializable(self):
        """测试可序列化为 JSON（Pydantic 关键能力）"""
        r = make_repo_info()
        report = RepoReport(repo=r, fetched_at="2026-07-22T10:00:00")
        json_str = report.model_dump_json()
        assert "facebook/react" in json_str
        assert '"stars":230000' in json_str
