#!/usr/bin/env python
"""DevSkillMapper 一键启动：llama.cpp + FastAPI 后端"""
import subprocess
import time
import sys
import os
import signal
import requests

# ── 配置 ──────────────────────────────────────────────
HOST = "127.0.0.1"
LLAMA_PORT = 8080
API_PORT = 8001
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LLAMA_SERVER = os.path.join(ROOT_DIR, "llama-cpp", "llama-server.exe")
MODEL_PATH = os.path.join(ROOT_DIR, "llama-cpp", "Qwen3.5-9B-Q4_K_M.gguf")

procs = []


def log(msg: str = "", **kw):
    print(msg, flush=True, **kw)


def wait_for(url: str, timeout: int = 180, label: str = "服务") -> bool:
    log(f"  等待 {label} 就绪", end="")
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(url, timeout=3).status_code == 200:
                log(" ✓")
                return True
        except Exception:
            pass
        log(".", end="")
        time.sleep(3)
    log(f" ✗ 超时 ({timeout}s)")
    return False


def cleanup(*_):
    log("\n正在关闭服务...")
    for p in procs:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            p.kill()
    log("已关闭")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    if not os.path.exists(LLAMA_SERVER):
        log(f"错误: 未找到 {LLAMA_SERVER}")
        sys.exit(1)
    if not os.path.exists(MODEL_PATH):
        log(f"错误: 未找到模型 {MODEL_PATH}")
        sys.exit(1)

    # ── 启动 llama.cpp ────────────────────────────────
    log("=" * 50)
    log("启动 llama.cpp 服务器")
    log("=" * 50)
    llama_proc = subprocess.Popen([
        LLAMA_SERVER, "-m", MODEL_PATH,
        "-ngl", "99", "-c", "4096",
        "--host", HOST, "--port", str(LLAMA_PORT),
        "--reasoning", "on",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    procs.append(llama_proc)

    if not wait_for(f"http://{HOST}:{LLAMA_PORT}/health", 300, "llama.cpp"):
        cleanup()

    # ── 启动 FastAPI ──────────────────────────────────
    log("\n" + "=" * 50)
    log("启动 FastAPI 后端")
    log("=" * 50)
    api_proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", HOST, "--port", str(API_PORT),
        "--log-level", "info",
    ], cwd=ROOT_DIR)
    procs.append(api_proc)

    if not wait_for(f"http://{HOST}:{API_PORT}/api/health", 15, "FastAPI"):
        cleanup()

    # ── 快速验证 ──────────────────────────────────────
    log("\n" + "=" * 50)
    log("服务就绪，快速验证")
    log("=" * 50)

    health = requests.get(f"http://{HOST}:{API_PORT}/api/health").json()
    log(f"  健康检查: {health['status']}")
    log(f"  缓存条目: {health['cache_entries']}")

    rate = requests.get(f"http://{HOST}:{API_PORT}/api/rate-limit").json()
    log(f"  API Token: {'有' if rate['has_token'] else '无'}")
    log(f"  剩余额度: {rate['remaining']}")

    log("\n" + "=" * 50)
    log(f"后端已启动")
    log(f"  FastAPI:  http://{HOST}:{API_PORT}")
    log(f"  llama:    http://{HOST}:{LLAMA_PORT}")
    log(f"  分析接口: http://{HOST}:{API_PORT}/api/analyze/{{owner}}/{{repo}}")
    log(f"  报告接口: POST http://{HOST}:{API_PORT}/api/report")
    log("=" * 50)
    log("按 Ctrl+C 停止\n")

    # ── 保持运行 ──────────────────────────────────────
    try:
        while True:
            time.sleep(1)
            for p in procs:
                if p.poll() is not None:
                    log(f"\n进程异常退出 (code={p.returncode})")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
