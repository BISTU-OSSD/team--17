"""
DevSkillMapper - 缓存层

提供双层缓存：内存缓存（快速）+ SQLite 持久缓存（可选），
减轻 GitHub API 限流压力（无 Token: 60 req/h，有 Token: 5000 req/h）。
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Optional

import aiosqlite

from .config import (
    CACHE_TTL_SECONDS,
    CACHE_MAX_ENTRIES,
    USE_SQLITE_CACHE,
    SQLITE_CACHE_PATH,
)


class _CacheEntry:
    """缓存条目"""
    __slots__ = ("data", "expires_at")
    data: Any
    expires_at: float


class CacheManager:
    """缓存管理器 —— 内存 + 可选 SQLite"""

    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}
        self._db: Optional[aiosqlite.Connection] = None
        self._db_ready = False

    # ── 初始化 ──────────────────────────────────────────

    async def init_db(self) -> None:
        """初始化 SQLite 持久缓存（按需）"""
        if not USE_SQLITE_CACHE:
            return
        self._db = await aiosqlite.connect(SQLITE_CACHE_PATH)
        await self._db.execute(
            "CREATE TABLE IF NOT EXISTS cache ("
            "  key TEXT PRIMARY KEY,"
            "  data TEXT NOT NULL,"
            "  expires_at REAL NOT NULL"
            ")"
        )
        await self._db.commit()
        self._db_ready = True

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._db:
            await self._db.close()
            self._db_ready = False

    # ── 缓存键构造 ──────────────────────────────────────

    @staticmethod
    def make_key(full_name: str, endpoint: str) -> str:
        """统一构造缓存键：owner/repo + API 端点"""
        owner, repo = full_name.split("/", 1)
        return f"{owner}/{repo}:{endpoint}"

    # ── 读写接口 ────────────────────────────────────────

    def _evict_lru(self) -> None:
        """内存缓存满时淘汰最早过期/最旧的条目"""
        if len(self._store) < CACHE_MAX_ENTRIES:
            return
        # 按过期时间排序，淘汰最早过期（或最旧的）
        now = time.time()
        expired = [k for k, v in self._store.items() if v.expires_at <= now]
        if expired:
            for k in expired:
                del self._store[k]
            return
        # 没有过期条目，淘汰最旧的一个
        oldest_key = min(self._store, key=lambda k: self._store[k].expires_at)
        del self._store[oldest_key]

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存：先内存、再 SQLite"""
        # 1) 内存
        entry = self._store.get(key)
        if entry is not None:
            if entry.expires_at > time.time():
                return entry.data
            del self._store[key]  # 过期淘汰

        # 2) SQLite
        if self._db_ready and self._db:
            cursor = await self._db.execute(
                "SELECT data, expires_at FROM cache WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            if row:
                data_str, expires_at = row
                if expires_at > time.time():
                    data = json.loads(data_str)
                    self._store[key] = _CacheEntry()
                    self._store[key].data = data
                    self._store[key].expires_at = expires_at
                    self._evict_lru()
                    return data
                # SQLite 中已过期 → 删除
                await self._db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await self._db.commit()

        return None

    async def set(self, key: str, data: Any, ttl: int = CACHE_TTL_SECONDS) -> None:
        """写入缓存"""
        expires_at = time.time() + ttl
        self._evict_lru()
        entry = _CacheEntry()
        entry.data = data
        entry.expires_at = expires_at
        self._store[key] = entry

        if self._db_ready and self._db:
            await self._db.execute(
                "INSERT OR REPLACE INTO cache (key, data, expires_at) VALUES (?, ?, ?)",
                (key, json.dumps(data, default=str), expires_at),
            )
            await self._db.commit()

    async def delete(self, key: str) -> None:
        """删除缓存条目"""
        self._store.pop(key, None)
        if self._db_ready and self._db:
            await self._db.execute("DELETE FROM cache WHERE key = ?", (key,))
            await self._db.commit()

    def clear_memory(self) -> None:
        """清空内存缓存"""
        self._store.clear()

    # ── 健康检查 ────────────────────────────────────────

    @property
    def memory_size(self) -> int:
        return len(self._store)


# 全局单例
cache = CacheManager()
