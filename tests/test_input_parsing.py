"""
测试 GitHub 仓库路径解析功能。
纯单元测试，不发起任何网络请求。
"""
import pytest
from app.github_client import _extract_owner_repo, GitHubClient


class TestExtractOwnerRepo:
    """_extract_owner_repo 函数测试"""

    def test_plain_owner_repo(self):
        """最基本的 owner/repo 格式"""
        assert _extract_owner_repo("facebook/react") == ("facebook", "react")

    def test_full_https_url(self):
        """完整 https URL"""
        assert _extract_owner_repo("https://github.com/facebook/react") == (
            "facebook",
            "react",
        )

    def test_git_suffix(self):
        """带 .git 后缀"""
        assert _extract_owner_repo("https://github.com/facebook/react.git") == (
            "facebook",
            "react",
        )

    def test_trailing_slash(self):
        """带末尾斜杠"""
        assert _extract_owner_repo("microsoft/vscode/") == ("microsoft", "vscode")

    def test_torvalds_linux(self):
        """实际仓库名"""
        assert _extract_owner_repo("torvalds/linux") == ("torvalds", "linux")

    def test_http_protocol(self):
        """http 协议（不带 s）"""
        assert _extract_owner_repo("http://github.com/x/y") == ("x", "y")

    def test_invalid_no_slash(self):
        """没有斜杠 - 应抛 ValueError"""
        with pytest.raises(ValueError):
            _extract_owner_repo("facebook")

    def test_empty_string(self):
        """空字符串 - 应抛 ValueError"""
        with pytest.raises(ValueError):
            _extract_owner_repo("")


class TestValidateInput:
    """GitHubClient.validate_input 公开接口测试"""

    def test_returns_full_name(self):
        """应该返回 'owner/repo' 格式的 full_name"""
        assert GitHubClient.validate_input("facebook/react") == "facebook/react"
        assert (
            GitHubClient.validate_input("https://github.com/facebook/react")
            == "facebook/react"
        )
        assert (
            GitHubClient.validate_input("https://github.com/facebook/react.git")
            == "facebook/react"
        )

    def test_invalid_input_raises(self):
        """无效输入应该抛出 ValueError"""
        with pytest.raises(ValueError):
            GitHubClient.validate_input("invalid")
        with pytest.raises(ValueError):
            GitHubClient.validate_input("")
