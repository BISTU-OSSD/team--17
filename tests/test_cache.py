"""
测试缓存模块（纯单元测试，不发网络请求）。
注意：CacheManager 的 get/set/delete 都是 async，必须用 await。
"""
import pytest
import asyncio
from app.cache import cache, CacheManager


class TestCacheManager:
    """CacheManager 单例缓存测试"""

    def setup_method(self):
        """每个测试前清空缓存"""
        cache.clear_memory()

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        await cache.set("test_key_1", {"data": 123}, ttl=60)
        result = await cache.get("test_key_1")
        assert result == {"data": 123}

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        await cache.set("ttl_key", "value", ttl=1)
        assert await cache.get("ttl_key") == "value"
        await asyncio.sleep(1.2)
        assert await cache.get("ttl_key") is None

    @pytest.mark.asyncio
    async def test_overwrite(self):
        await cache.set("overwrite_key", "old", ttl=60)
        await cache.set("overwrite_key", "new", ttl=60)
        assert await cache.get("overwrite_key") == "new"

    @pytest.mark.asyncio
    async def test_missing_key_returns_none(self):
        result = await cache.get("definitely_not_exists_xyz")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self):
        await cache.set("to_delete", "value", ttl=60)
        assert await cache.get("to_delete") == "value"
        await cache.delete("to_delete")
        assert await cache.get("to_delete") is None

    @pytest.mark.asyncio
    async def test_complex_data_types(self):
        """支持复杂数据结构"""
        data = {
            "list": [1, 2, 3],
            "dict": {"nested": True},
            "string": "hello",
        }
        await cache.set("complex", data, ttl=60)
        assert await cache.get("complex") == data


class TestMakeKey:
    """缓存键构造器测试"""

    def test_make_key(self):
        assert (
            CacheManager.make_key("facebook/react", "repo_info")
            == "facebook/react:repo_info"
        )

    def test_make_key_with_slash_in_name(self):
        # 实际不会出现斜杠在 repo 名中
        assert (
            CacheManager.make_key("owner/repo", "endpoint")
            == "owner/repo:endpoint"
        )
