"""一键启动：先启动 llama.cpp server，再运行分析程序"""

import subprocess
import time
import sys
import os
import requests
from config import LLAMA_SERVER, MODEL_PATH, HOST, PORT
from config import check_environment

HEALTH_URL = f"http://{HOST}:{PORT}/health"


def wait_server(timeout=120):
    print("等待模型加载...", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(HEALTH_URL, timeout=2)
            if resp.status_code == 200:
                print(" 就绪!")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(2)
    print("\n启动超时")
    return False


def main():
    check_environment()
    # 检查参数
    if len(sys.argv) == 1:
        # 交互模式: 启动流式对话
        mode = "chat"
    elif len(sys.argv) == 3:
        # 分析模式
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        
        # 验证输入存在
        if not os.path.exists(input_path):
            print(f"错误: 输入路径不存在: {input_path}")
            sys.exit(1)
        
        # 判断是批量还是单文件
        if os.path.isdir(input_path):
            mode = "batch"
        else:
            mode = "analyze"
            
            # 验证输出路径有效
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    print(f"错误: 无法创建输出目录: {e}")
                    sys.exit(1)
    else:
        print("用法:")
        print("  python run_llm.py                                    # 交互对话模式")
        print("  python run_llm.py <输入文件> <输出文件>               # 单文件分析")
        print("  python run_llm.py <输入目录> <输出目录>               # 批量分析")
        print("")
        print("示例:")
        print("  python run_llm.py examples\\sample_input.txt result.json")
        print("  python run_llm.py projects/ results/")
        sys.exit(1)

    # 启动服务器
    print("启动 llama.cpp 服务器...")
    server_proc = subprocess.Popen([
        LLAMA_SERVER, "-m", MODEL_PATH, "-ngl", "99", "-c", "4096",
        "--host", HOST, "--port", str(PORT), "--reasoning", "on",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        if not wait_server():
            server_proc.terminate()
            sys.exit(1)

        if mode == "batch":
            # 批量分析模式
            script = os.path.join(os.path.dirname(__file__), "batch_analyze.py")
            subprocess.run([sys.executable, script, input_path, output_path])
        elif mode == "analyze":
            # 单文件分析模式
            script = os.path.join(os.path.dirname(__file__), "analyze.py")
            subprocess.run([sys.executable, script, input_path, output_path])
        else:
            # 交互对话模式
            script = os.path.join(os.path.dirname(__file__), "llama_stream.py")
            subprocess.run([sys.executable, script])

    except KeyboardInterrupt:
        print("\n\n正在关闭...")
    finally:
        server_proc.terminate()
        server_proc.wait()
        print("Server 已关闭")


if __name__ == "__main__":
    main()
