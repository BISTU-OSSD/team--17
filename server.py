"""FastAPI HTTP 服务器 — 对接前端与 LLM (本地/GPU服务器运行版)"""

import sys
import os
import re
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import certifi
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# SSL 验证：Windows 环境默认关闭
VERIFY_SSL = os.getenv("VERIFY_SSL", "false").lower() != "false"

# GitHub Token（可选，提高 API 速率限制）
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# GPU 服务器 LLM 接口地址（优先从环境变量读取）
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://raving-tubeless-greeting.ngrok-free.dev")

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from analyzer import analyze_github_project

app = FastAPI(title="GitHub 项目体检 API", version="1.0.0")

# 允许跨域（包含 ngrok 和 Railway 域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_GITHUB_API = "https://api.github.com"
_HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    _HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"
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


async def fetch_github_repo_details(owner: str, repo: str) -> dict:
    """获取 GitHub 仓库详细数据，用于前端展示"""
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

        # 获取语言列表（带百分比）
        languages = []
        languages_url = data.get("languages_url", "")
        if languages_url:
            try:
                lang_resp = await client.get(languages_url, headers=_HEADERS, timeout=10)
                if lang_resp.is_success:
                    lang_data = lang_resp.json()
                    total_bytes = sum(lang_data.values())
                    for lang, bytes_count in lang_data.items():
                        languages.append({
                            "language": lang,
                            "percentage": round(bytes_count / total_bytes * 100, 1) if total_bytes > 0 else 0
                        })
            except httpx.RequestError:
                pass

        # 获取贡献者信息
        contributors = {"total_contributors": 0, "active_30d_contributors": 0, "bus_factor": 0}
        contributors_url = data.get("contributors_url", "")
        if contributors_url:
            try:
                contrib_resp = await client.get(f"{contributors_url}?per_page=100", headers=_HEADERS, timeout=10)
                if contrib_resp.is_success:
                    contrib_data = contrib_resp.json()
                    contributors["total_contributors"] = len(contrib_data)
            except httpx.RequestError:
                pass

        # 获取 commits 信息
        commits = {"commits_last_30_days": 0, "commit_frequency_per_week": 0}
        commits_url = f"{_GITHUB_API}/repos/{owner}/{repo}/commits"
        try:
            commits_resp = await client.get(f"{commits_url}?per_page=100", headers=_HEADERS, timeout=10)
            if commits_resp.is_success:
                commits_data = commits_resp.json()
                commits["commits_last_30_days"] = len(commits_data)
                commits["commit_frequency_per_week"] = round(len(commits_data) / 4, 1)
        except httpx.RequestError:
            pass

        # 获取 issues 信息
        issues = {"close_rate": 0}
        issues_url = f"{_GITHUB_API}/repos/{owner}/{repo}/issues?state=all&per_page=100"
        try:
            issues_resp = await client.get(issues_url, headers=_HEADERS, timeout=10)
            if issues_resp.is_success:
                issues_data = issues_resp.json()
                total_issues = len(issues_data)
                closed_issues = sum(1 for i in issues_data if i.get("state") == "closed")
                issues["close_rate"] = round(closed_issues / total_issues, 2) if total_issues > 0 else 0
        except httpx.RequestError:
            pass

    return {
        "languages": languages,
        "contributors": contributors,
        "commits": commits,
        "issues": issues,
        "star_count": data.get("stargazers_count", 0),
        "fork_count": data.get("forks_count", 0),
        "description": data.get("description", ""),
        "license": data.get("license", {}).get("spdx_id", "未知") if data.get("license") else "未知",
    }


@app.get("/api/analyze/{owner}/{repo}")
async def analyze_repo(owner: str, repo: str):
    """同步分析 GitHub 仓库"""
    if not _REPO_RE.match(f"{owner}/{repo}"):
        raise HTTPException(status_code=400, detail="仓库路径格式无效")

    repo_details = await fetch_github_repo_details(owner, repo)
    text_content = await fetch_github_repo_info(owner, repo)

    try:
        result = analyze_github_project(text_content)
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "分析失败"))

        result["languages"] = repo_details["languages"]
        result["contributors"] = repo_details["contributors"]
        result["commits"] = repo_details["commits"]
        result["issues"] = repo_details["issues"]
        result["star_count"] = repo_details["star_count"]
        result["fork_count"] = repo_details["fork_count"]
        result["description"] = repo_details["description"]
        result["license"] = repo_details["license"]
        return result
    except Exception as e:
        return {
            "status": "success",
            "repo": {
                "full_name": f"{owner}/{repo}",
                "description": repo_details.get("description", "LLM 分析服务暂时不可用"),
                "stargazers_count": repo_details.get("star_count", 0),
                "forks_count": repo_details.get("fork_count", 0),
                "language": repo_details["languages"][0]["language"] if repo_details["languages"] else "未知"
            },
            "languages": repo_details["languages"],
            "contributors": repo_details["contributors"],
            "commits": repo_details["commits"],
            "issues": repo_details["issues"],
            "star_count": repo_details["star_count"],
            "fork_count": repo_details["fork_count"],
            "analysis": {
                "total_score": 5.0,
                "scores": {
                    "活跃度": 5.0, "社区响应": 5.0, "文档质量": 5.0,
                    "代码规模": 5.0, "稳定性": 5.0, "影响力": 5.0
                },
                "summary": "LLM 分析服务暂时不可用，请稍后再试。",
                "suggestions": ["等待 LLM 服务恢复后重新分析"]
            }
        }


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "GitHub 项目体检 API", "version": "1.0.0"}


# ========== 流式输出端点 ==========

from llama_chat import SYSTEM_PROMPT


def get_current_date() -> str:
    return "today is " + datetime.now().strftime("%Y/%m/%d")


@app.get("/api/stream/{owner}/{repo}")
async def stream_analysis(owner: str, repo: str):
    """流式分析 GitHub 仓库，实时返回 LLM 思考过程"""

    async def event_generator(owner: str, repo: str):
        try:
            yield f"data: {json.dumps({'type': 'start', 'message': '开始分析...'})}\n\n"
            yield f"data: {json.dumps({'type': 'step', 'message': '正在获取 GitHub 仓库数据...'})}\n\n"

            text_content = await fetch_github_repo_info(owner, repo)
            repo_details = await fetch_github_repo_details(owner, repo)

            yield f"data: {json.dumps({'type': 'step', 'message': '数据获取完成，开始 LLM 分析...'})}\n\n"

            prompt = SYSTEM_PROMPT + "\n" + get_current_date() + "\n" + text_content

            from config import MODEL_PATH

            # 拼接正确的 GPU 服务器接口地址
            server_url = f"{LLM_BASE_URL.rstrip('/')}/v1/chat/completions"

            # 准备请求头（包含绕过 ngrok 警告的 Header）
            llm_headers = {
                "ngrok-skip-browser-warning": "69420",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                async with client.stream(
                    "POST",
                    server_url,
                    headers=llm_headers,
                    json={
                        "model": MODEL_PATH,
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": "请评估以上GitHub项目"},
                        ],
                        "temperature": 0.6,
                        "max_tokens": 8192,
                        "stream": True,
                        "reasoning_effort": "high",
                    }
                ) as resp:
                    resp.raise_for_status()

                    thinking = True
                    answer_parts = []
                    last_ping_time = asyncio.get_event_loop().time()

                    async for raw_line in resp.aiter_lines():
                        # --- SSE 心跳机制：每 5 秒自动发送一次，防止网络超时切断 ---
                        current_time = asyncio.get_event_loop().time()
                        if current_time - last_ping_time > 5.0:
                            yield ": ping\n\n"
                            last_ping_time = current_time

                        line = raw_line.strip()
                        if not line or not line.startswith("data: "):
                            continue

                        data = line[6:].strip()
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            if not chunk.get("choices"):
                                continue

                            delta = chunk["choices"][0].get("delta", {})

                            # 1. 思考过程
                            if delta.get("reasoning_content"):
                                yield f"data: {json.dumps({'type': 'thinking', 'content': delta['reasoning_content']})}\n\n"

                            # 2. 正式回复内容
                            if delta.get("content"):
                                if thinking:
                                    thinking = False
                                answer_parts.append(delta["content"])
                                yield f"data: {json.dumps({'type': 'answer', 'content': delta['content']})}\n\n"
                        except json.JSONDecodeError:
                            continue

            # 最终结果解析
            final_answer = "".join(answer_parts)
            try:
                cleaned = final_answer
                if "```json" in cleaned:
                    start = cleaned.find("```json") + 7
                    end = cleaned.rfind("```")
                    if end != -1 and end > start:
                        cleaned = cleaned[start:end].strip()
                elif "```" in cleaned:
                    start = cleaned.find("```") + 3
                    end = cleaned.rfind("```")
                    if end != -1 and end > start:
                        cleaned = cleaned[start:end].strip()

                result = json.loads(cleaned)

                result["languages"] = repo_details["languages"]
                result["contributors"] = repo_details["contributors"]
                result["commits"] = repo_details["commits"]
                result["issues"] = repo_details["issues"]
                result["star_count"] = repo_details["star_count"]
                result["fork_count"] = repo_details["fork_count"]
                result["description"] = repo_details["description"]
                result["license"] = repo_details["license"]

                yield f"data: {json.dumps({'type': 'done', 'result': result})}\n\n"
            except Exception:
                # 容错保底：解析失败时尽量返回基础数据
                fallback_result = {
                    "raw_answer": final_answer,
                    "languages": repo_details["languages"],
                    "contributors": repo_details["contributors"],
                    "commits": repo_details["commits"],
                    "issues": repo_details["issues"],
                    "star_count": repo_details["star_count"],
                    "fork_count": repo_details["fork_count"],
                    "description": repo_details["description"],
                    "license": repo_details["license"],
                }
                yield f"data: {json.dumps({'type': 'done', 'result': fallback_result})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(owner, repo),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.get("/api/stream/health")
async def stream_health():
    return {"status": "ok", "endpoint": "stream", "version": "1.0.0"}
