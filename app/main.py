"""
DevSkillMapper - FastAPI 后端入口

提供 REST API：
  POST /api/report           — 获取仓库体检报告
  GET  /api/analyze/{o}/{r}  — 获取报告 + LLM 分析（前端对接）
  GET  /api/health            — 健康检查
  GET  /api/rate-limit        — 查询 API 限流状态
  DELETE /api/cache           — 清空缓存
"""
from __future__ import annotations

import asyncio
import sys
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# 确保 src 模块可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.json_to_text import convert_json_to_text
from src.analyzer import analyze_github_project
from llama_chat import stream_chat_chunks, SYSTEM_PROMPT as LLM_SYSTEM_PROMPT

from .cache import cache
from .github_client import (
    GitHubClient,
    RepoNotFoundError,
    RateLimitExceededError,
    AuthenticationError,
    GitHubAPIError,
)


# ── 请求模型 ─────────────────────────────────────────────

class ReportRequest(BaseModel):
    """体检报告请求"""
    repo: str = Field(
        ...,
        description="仓库全名或 URL，例如 facebook/react 或 https://github.com/facebook/react",
        examples=["facebook/react", "https://github.com/torvalds/linux"],
    )
    token: Optional[str] = Field(
        None,
        description="可选 GitHub Personal Access Token，用于提升 API 额度",
    )
    force_refresh: bool = Field(False, description="是否强制刷新缓存")


# ── 响应模型 ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_type: str
    status_code: int


# ── 生命周期 ─────────────────────────────────────────────

_client: Optional[GitHubClient] = None


def _get_client(token: str = "") -> GitHubClient:
    """获取或创建客户端实例（每次请求按需创建，带 token 隔离）"""
    global _client
    if token:
        # 用户传了 token 则创建独立实例
        return GitHubClient(token=token)
    if _client is None:
        _client = GitHubClient()
    return _client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await cache.init_db()
    yield
    await cache.close()
    if _client:
        await _client.close()


# ── FastAPI 应用 ─────────────────────────────────────────

app = FastAPI(
    title="DevSkillMapper API",
    description="开源仓库健康度评估与推荐平台 - 后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 开发环境允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API 端点 ─────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "DevSkillMapper",
        "version": "1.0.0",
        "cache_entries": cache.memory_size,
    }


@app.get("/api/rate-limit")
async def rate_limit_status():
    """查询当前 API 限流状态"""
    client = _get_client()
    return client.rate_limit_info


@app.post("/api/report")
async def get_repo_report(req: ReportRequest):
    """
    获取仓库完整体检原始数据。

    输入仓库路径（owner/repo 或完整 URL），
    返回结构化报告，包含仓库信息、语言分布、Commit 活跃度、
    Issue/PR 统计、贡献者画像、文档质量、发布信息。

    这是算法模块和前端可视化的数据输入。
    """
    # 1. 校验输入
    try:
        full_name = GitHubClient.validate_input(req.repo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. 获取客户端并拉取数据
    client = _get_client(token=req.token or "")

    try:
        report = await client.get_full_report(full_name, force_refresh=req.force_refresh)
    except RepoNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "detail": str(e),
                "error_type": "repo_not_found",
                "status_code": 404,
            },
        )
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail={
                "detail": str(e),
                "error_type": "rate_limit_exceeded",
                "status_code": 429,
                "reset_at": e.reset_at.isoformat() if e.reset_at else None,
            },
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "detail": str(e),
                "error_type": "authentication_error",
                "status_code": 401,
            },
        )
    except GitHubAPIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "detail": str(e),
                "error_type": "github_api_error",
                "status_code": 502,
            },
        )

    # 3. 返回
    return {
        "success": True,
        "data": report.model_dump(),
        "rate_limit": client.rate_limit_info,
    }


@app.get("/api/analyze/{owner}/{repo}")
async def analyze_repo(owner: str, repo: str):
    """
    流式分析 GitHub 仓库（SSE）。

    事件类型：
      step     — 处理步骤进度
      thinking — LLM 思考过程
      content  — LLM 正式回复
      result   — 最终完整结果
      error    — 错误
    """
    import re, json as _json
    from datetime import datetime

    if not re.match(r"^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$", f"{owner}/{repo}"):
        raise HTTPException(status_code=400, detail="仓库路径格式无效")

    full_name = f"{owner}/{repo}"
    client = _get_client()

    def sse(event: str, data) -> str:
        return f"event: {event}\ndata: {_json.dumps(data, ensure_ascii=False)}\n\n"

    async def generate():
        # Step 1: 校验
        yield sse("step", {"step": "validating", "message": "校验仓库路径..."})

        # Step 2: 获取 GitHub 数据
        yield sse("step", {"step": "fetching", "message": "正在从 GitHub 获取仓库数据..."})
        try:
            report = await client.get_full_report(full_name)
        except RepoNotFoundError as e:
            yield sse("error", {"message": str(e)})
            return
        except RateLimitExceededError as e:
            yield sse("error", {"message": str(e)})
            return
        except GitHubAPIError as e:
            yield sse("error", {"message": str(e)})
            return

        report_dict = report.model_dump()
        yield sse("step", {"step": "fetched", "message": f"已获取 {full_name} 数据"})

        # Step 3: 转文本
        yield sse("step", {"step": "converting", "message": "转换为分析文本..."})
        text_content = convert_json_to_text(report_dict)
        yield sse("step", {"step": "converted", "message": "文本转换完成"})

        # Step 4: LLM 分析（流式）
        yield sse("step", {"step": "analyzing", "message": "AI 正在分析，请稍候..."})
        loop = asyncio.get_running_loop()

        thinking_text = ""
        content_text = ""

        def run_stream():
            nonlocal thinking_text, content_text
            for chunk in stream_chat_chunks(LLM_SYSTEM_PROMPT, text_content):
                if chunk["type"] == "thinking":
                    thinking_text += chunk["text"]
                elif chunk["type"] == "content":
                    content_text += chunk["text"]

        await loop.run_in_executor(None, run_stream)

        # 用完整文本做一次非流式调用拿结构化结果
        analysis = await loop.run_in_executor(None, analyze_github_project, text_content)

        # 发送思考和回复内容
        if thinking_text:
            yield sse("thinking", {"text": thinking_text})
        if content_text:
            yield sse("content", {"text": content_text})

        # Step 5: 完成
        yield sse("step", {"step": "done", "message": "分析完成"})
        yield sse("result", {
            "success": True,
            "report": report_dict,
            "analysis": analysis,
            "rate_limit": client.rate_limit_info,
        })

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.delete("/api/cache")
async def clear_cache():
    """清空所有缓存"""
    cache.clear_memory()
    if cache._db_ready and cache._db:
        await cache._db.execute("DELETE FROM cache")
        await cache._db.commit()
    return {"success": True, "message": "缓存已清空"}


# ── 全局异常兜底 ─────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    """HTTPException 处理器 —— 直接返回 detail，避免被 Exception 处理器覆盖"""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    """未预料异常的兜底处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": f"服务器内部错误: {str(exc)}",
            "error_type": "internal_error",
            "status_code": 500,
        },
    )


# ── 入口 ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
