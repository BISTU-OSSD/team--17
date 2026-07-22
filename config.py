import os
from dotenv import load_dotenv

load_dotenv()

# 项目根目录（config.py 所在目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LLAMA_SERVER = os.getenv("LLAMA_SERVER") or os.path.join(ROOT_DIR, "llama-cpp", "llama-server.exe")
MODEL_PATH = os.getenv("MODEL_PATH") or os.path.join(ROOT_DIR, "llama-cpp", "Qwen3.5-9B-Q4_K_M.gguf")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8080"))

def check_environment():
    """检查运行环境"""

    if not os.path.exists(LLAMA_SERVER):
        raise FileNotFoundError(
            f"未找到 llama-server.exe\n请检查：{LLAMA_SERVER}"
        )

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"未找到模型文件\n请检查：{MODEL_PATH}"
        )