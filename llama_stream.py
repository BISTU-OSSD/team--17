"""检测 llama.cpp 流式输出"""

from datetime import datetime
import requests
import json

SERVER_URL = "http://localhost:8080/v1/chat/completions"
MODEL_PATH = r"D:\20260721\llama-cpp\Qwen3.5-9B-Q4_K_M.gguf"

SYSTEM_PROMPT = """你是一个GitHub项目评估专家。请根据输入的GitHub项目数据，从以下6个维度进行评分分析，每个维度满分10分：

1. 代码质量 — 代码规范性、可读性、架构设计、测试覆盖率
2. 社区活跃度 — Issue/PR数量、响应速度、贡献者数量
3. 更新频率 — 近期提交频率、版本发布节奏
4. 文档完整性 — README、API文档、示例代码、使用指南
5. 安全状况 — 已知漏洞、依赖安全性、安全更新及时性
6. 社区影响力 — Star数、Fork数、引用情况、行业认可度

你应该：
- 基于输入数据客观评分，有理有据
- 说明部分给出具体依据，而非空泛评价
- 总结建议给出可操作的改进建议

你不能：
- 凭空编造不存在的数据
- 在没有依据的情况下给高分或低分
- 输出JSON以外的任何内容

请严格按以下JSON格式输出，不要输出其他内容：
```json
{
  "项目名称": "xxx",
  "评分": {
    "代码质量": {"分数": 0, "说明": "..."},
    "社区活跃度": {"分数": 0, "说明": "..."},
    "更新频率": {"分数": 0, "说明": "..."},
    "文档完整性": {"分数": 0, "说明": "..."},
    "安全状况": {"分数": 0, "说明": "..."},
    "社区影响力": {"分数": 0, "说明": "..."}
  },
  "总结建议": "..."
}
```"""


def get_current_date() -> str:
    return "today is " + datetime.now().strftime("%Y/%m/%d")


MOCK_REPO_CONTENT = """
项目名称: llama.cpp
GitHub地址: https://github.com/ggml-org/llama.cpp
Star数: 80000+
Fork数: 12000+
最近更新: 2026-07-20
主要语言: C++
许可证: MIT

README摘要:
llama.cpp 是一个纯 C/C++ 实现的 LLM 推理库，支持在多种硬件上运行。

特点:
- 无需依赖，纯C/C++实现
- 支持GGUF量化格式
- 提供HTTP服务器和命令行工具
- 支持多种模型架构

最近Issue数量: 200+
最近PR数量: 50+
贡献者数量: 500+
测试覆盖率: 60%
文档完善度: 中等
已知安全漏洞: 无高危漏洞
"""


def stream_chat(system_prompt: str, content: str):
    """流式输出"""
    resp = requests.post(SERVER_URL, json={
        "model": MODEL_PATH,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": True,
        "reasoning_effort": "high",
    }, stream=True)
    resp.raise_for_status()

    thinking = True
    print("思考中...\n", flush=True)
    for line in resp.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        data = line[6:]
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        delta = chunk["choices"][0]["delta"]
        if "reasoning_content" in delta and delta["reasoning_content"]:
            print(delta["reasoning_content"], end="", flush=True)
        if "content" in delta and delta["content"]:
            if thinking:
                print("\n\n--- 回复 ---\n", flush=True)
                thinking = False
            print(delta["content"], end="", flush=True)
    print()


def main():
    print("=== GitHub 项目评估（流式输出）===\n")

    file_path = input("仓库数据文件路径（直接回车用模拟数据）: ").strip()
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                repo_content = f.read()
        except Exception as e:
            print(f"读取失败: {e}，使用模拟数据")
            repo_content = MOCK_REPO_CONTENT
    else:
        repo_content = MOCK_REPO_CONTENT

    prompt = SYSTEM_PROMPT + "\n" + get_current_date() + "\n" + repo_content

    print("\n分析中...\n")
    stream_chat(prompt, "请评估以上GitHub项目")


if __name__ == "__main__":
    main()
