"""FastAPI HTTP 服务器 — 对接前端的 API 接口"""

import sys
import os
import re

import certifi
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# SSL 验证：默认开启；部分 Windows 环境需设 VERIFY_SSL=false
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() != "false"

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from analyzer import analyze_github_project

app = FastAPI(title="GitHub 项目体检 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_GITHUB_API = "https://api.github.com"
_HEADERS = {"Accept": "application/vnd.github.v3+json"}
_REPO_RE = re.compile(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$")


async def fetch_github_repo_info(owner: str, repo: str) -> str:
    """通过 GitHub API 获取仓库基本信息，构造分析输入文本"""
    api_url = f"{_GITHUB_API}/repos/{owner}/{repo}"

    ssl_ctx = certifi.where() if VERIFY_SSL else False
    async with httpx.AsyncClient(timeout=15, follow_redirects=True, verify=ssl_ctx) as client:
        try:
            resp = await client.get(api_url, headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"GitHub API 返回错误: {e.response.status_code}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"无法访问 GitHub API: {e}")

        # 获取语言列表
        languages: list[str] = []
        languages_url = data.get("languages_url", "")
        if languages_url:
            try:
                lang_resp = await client.get(languages_url, headers=_HEADERS, timeout=10)
                if lang_resp.is_success:
                    languages = list(lang_resp.json().keys())
            except httpx.RequestError:
                pass

    issues_count = data.get("open_issues_count", 0)

    text = f"""项目名称: {data.get("full_name", f"{owner}/{repo}")}
GitHub地址: https://github.com/{owner}/{repo}
Star数: {data.get("stargazers_count", 0)}
Fork数: {data.get("forks_count", 0)}
主要语言: {", ".join(languages) if languages else "未知"}
许可证: {data.get("license", {}).get("spdx_id", "未知") if data.get("license") else "未知"}
最近更新: {data.get("updated_at", "未知")}
描述: {data.get("description", "无")}
最近Issue数量: {issues_count}
"""

    return text


@app.get("/api/analyze/{owner}/{repo}")
async def analyze_repo(owner: str, repo: str):
    """分析 GitHub 仓库，返回评分结果"""
    if not _REPO_RE.match(f"{owner}/{repo}"):
        raise HTTPException(status_code=400, detail="仓库路径格式无效")

    text_content = await fetch_github_repo_info(owner, repo)
    result = analyze_github_project(text_content)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "分析失败"))

    return result


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "GitHub 项目体检 API", "version": "1.0.0"}
