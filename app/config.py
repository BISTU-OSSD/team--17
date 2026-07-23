"""
DevSkillMapper - 全局配置
"""
import os
from dotenv import load_dotenv, find_dotenv

# 确保从当前文件所在目录的 .env 加载
load_dotenv(find_dotenv())

# GitHub API 基础配置
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# SSL 验证：Windows 开发环境 certifi 证书链不完整，默认 false
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() != "false"

# 缓存配置
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "600"))      # 默认 10 分钟
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "200"))
USE_SQLITE_CACHE = os.getenv("USE_SQLITE_CACHE", "false").lower() == "true"
SQLITE_CACHE_PATH = os.getenv("SQLITE_CACHE_PATH", "cache.db")

# 请求配置
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "1.5"))

# 无 Token 时更保守的并发限制
DEFAULT_PER_PAGE = 30
MAX_PER_PAGE = 100
