"""FastAPI HTTP 服务器 — 对接前端的 API 接口"""

import sys
import os
import requests as req

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_github_project
from validators import validate_analysis_result

app = FastAPI(title="GitHub 项目体检 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_github_repo_info(owner: str, repo: str) -> str:
    """通过 GitHub API 获取仓库基本信息，构造分析输入文本"""
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        resp = req.get(api_url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        data = resp.json()
    except req.RequestException as e:
        raise HTTPException(status_code=502, detail=f"无法访问 GitHub API: {e}")

    # 获取语言列表
    languages_url = data.get("languages_url", "")
    languages = []
    if languages_url:
        try:
            lang_resp = req.get(languages_url, headers=headers, timeout=10, verify=False)
            if lang_resp.ok:
                languages = list(lang_resp.json().keys())
        except req.RequestException:
            pass

    # 获取最近 Issues 和 PRs 数量
    issues_count = data.get("open_issues_count", 0)

    # 构造输入文本（与 analyzer.py 中期望的格式一致）
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
def analyze_repo(owner: str, repo: str):
    """分析 GitHub 仓库，返回评分结果"""
    text_content = fetch_github_repo_info(owner, repo)
    result = analyze_github_project(text_content)

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "分析失败"))

    return result


@app.get("/api/health")
def health():
    return {"status": "ok"}
