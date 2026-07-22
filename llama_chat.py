"""向本地 llama.cpp 发送内容并获取回复（单轮）"""

from datetime import datetime
import requests
import sys
import json
from config import MODEL_PATH, HOST, PORT

SERVER_URL = f"http://{HOST}:{PORT}/v1/chat/completions"

SYSTEM_PROMPT = """你是一个GitHub项目评估专家。请根据输入的GitHub项目数据，从以下6个维度进行评分分析，每个维度满分10分。

## 评分维度与标准

1. code_quality（代码质量）— 代码规范性、可读性、架构设计、测试覆盖率
   - 8-10分：CI/CD完善、测试覆盖率>80%、代码风格统一、架构清晰
   - 5-7分：有测试、代码可读性好、架构基本合理
   - 0-4分：缺少测试、代码混乱、架构不清晰

2. community_activity（社区活跃度）— Issue/PR数量、响应速度、贡献者数量
   - 8-10分：Issue响应<24h、贡献者>50人、PR活跃
   - 5-7分：Issue有回复、贡献者>10人
   - 0-4分：Issue长期无回复、贡献者很少

3. update_frequency（更新频率）— 近期提交频率、版本发布节奏
   - 8-10分：每周有提交、定期发布版本
   - 5-7分：每月有提交、有版本发布
   - 0-4分：超过3个月无更新

4. documentation（文档完整性）— README、API文档、示例代码、使用指南
   - 8-10分：README完整、有API文档、有示例代码、有使用指南
   - 5-7分：README基本完整、有部分文档
   - 0-4分：README简陋或缺失、无其他文档

5. security（安全状况）— 已知漏洞、依赖安全性、安全更新及时性
   - 8-10分：无高危漏洞、依赖安全、及时更新
   - 5-7分：有已知漏洞但已修复、依赖基本安全
   - 0-4分：有未修复的高危漏洞、依赖不安全

6. community_impact（社区影响力）— Star数、Fork数、引用情况、行业认可度
   - 8-10分：Star>10000、被广泛引用
   - 5-7分：Star>1000、有一定影响力
   - 0-4分：Star<100、影响力有限

## 输出要求

你应该：
- 基于输入数据客观评分，严格按上述标准执行
- 请给出大致评分即可，不必过度纠察细节
- detail字段给出具体中文依据，引用输入数据中的事实
- summary字段给出可操作的中文改进建议

你不能：
- 凭空编造不存在的数据
- 在没有依据的情况下给高分或低分
- 输出JSON以外的任何内容

请严格按以下JSON格式输出，键名必须是英文，detail和summary内容用中文：
```json
{
  "project_name": "xxx",
  "scores": {
    "code_quality": {"score": 0, "detail": "具体中文说明"},
    "community_activity": {"score": 0, "detail": "具体中文说明"},
    "update_frequency": {"score": 0, "detail": "具体中文说明"},
    "documentation": {"score": 0, "detail": "具体中文说明"},
    "security": {"score": 0, "detail": "具体中文说明"},
    "community_impact": {"score": 0, "detail": "具体中文说明"}
  },
  "summary": "中文总结建议"
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
llama.cpp 是一个纯 C/C++ 实现的 LLM 推理库，支持在多种硬件上运行：
- CPU (x86, ARM)
- NVIDIA GPU (CUDA)
- AMD GPU (ROCm/HIP)
- Apple Silicon (Metal)
- Intel GPU (SYCL)
- Qualcomm (OpenCL)

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


def chat(system_prompt: str, content: str) -> str:
    """发送消息并获取回复（非流式）"""
    resp = requests.post(SERVER_URL, json={
        "model": MODEL_PATH,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.6,
        "max_tokens": 8192,
        "reasoning_effort": "high",
    }, timeout=30)
    resp.raise_for_status()
    msg = resp.json()["choices"][0]["message"]
    thinking = msg.get("reasoning_content", "")
    answer = msg.get("content", "")
    if thinking:
        print(f"[思考过程]\n{thinking}\n")
    return answer


def stream_chat(system_prompt: str, content: str) -> str:
    """流式发送消息并获取回复，实时输出思考过程"""
    resp = requests.post(SERVER_URL, json={
        "model": MODEL_PATH,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": 0.6,
        "max_tokens": 8192,
        "stream": True,
        "reasoning_effort": "high",
    }, stream=True, timeout=30)
    resp.raise_for_status()

    thinking = True
    answer_parts = []
    
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
        
        # 流式输出思考过程
        if "reasoning_content" in delta and delta["reasoning_content"]:
            print(delta["reasoning_content"], end="", flush=True)
        
        # 收集正式回复内容
        if "content" in delta and delta["content"]:
            if thinking:
                print("\n\n--- 回复 ---\n", flush=True)
                thinking = False
            print(delta["content"], end="", flush=True)
            answer_parts.append(delta["content"])
    
    print()
    return "".join(answer_parts)


def load_repo_content(file_path: str = None) -> str:
    """加载仓库内容，如果指定文件则读取文件，否则使用模拟数据"""
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            print("使用模拟数据继续测试...")
            return MOCK_REPO_CONTENT
    return MOCK_REPO_CONTENT


def main():
    print("=== GitHub 项目评估工具 ===")
    print("直接回车使用模拟数据，或输入文件路径\n")

    file_path = input("仓库数据文件路径（可选）: ").strip()
    repo_content = load_repo_content(file_path if file_path else None)

    prompt = SYSTEM_PROMPT + "\n" + get_current_date() + "\n" + repo_content

    print("\n分析中...\n")
    print(chat(prompt, "请评估以上GitHub项目"))


if __name__ == "__main__":
    main()
