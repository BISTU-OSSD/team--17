"""向本地 llama.cpp 发送内容并获取回复（单轮）"""

from datetime import datetime
import requests
import sys
import json
from config import MODEL_PATH, LLAMA_SERVER_URL

SERVER_URL = LLAMA_SERVER_URL

SYSTEM_PROMPT = """你是一个GitHub项目评估专家。请根据输入的GitHub项目数据，从以下6个维度进行评分分析，每个维度满分10分。

## 评分维度与标准

### 1. code_quality（代码质量）

评估项目的代码规范性、可读性、架构设计、测试覆盖率。

| 分数 | 标准 |
|------|------|
| 9-10 | CI/CD完善（有GitHub Actions/GitLab CI）、测试覆盖率>80%、代码风格统一（有lint配置）、架构清晰（模块化设计）、有代码审查流程 |
| 7-8 | 有测试（覆盖率50-80%）、代码可读性好、架构基本合理、有部分CI配置 |
| 5-6 | 有基本测试、代码可读性一般、架构简单但可用 |
| 3-4 | 测试很少或无测试、代码混乱、架构不清晰 |
| 1-2 | 无测试、代码质量差、难以维护 |
| 0 | 无法评估或代码完全不可用 |

判断依据：
- 查找是否有.github/workflows、.gitlab-ci.yml、Makefile等CI配置
- 查找测试文件（test_*.py、*_test.go、*.test.js等）
- 查找配置文件（.eslintrc、.prettierrc、pyproject.toml等）
- 查找README中的测试说明

### 2. community_activity（社区活跃度）

评估项目的Issue/PR处理能力、响应速度、贡献者活跃度。

| 分数 | 标准 |
|------|------|
| 9-10 | Issue平均响应<24h、贡献者>100人、PR合并及时（<7天）、有活跃的讨论区 |
| 7-8 | Issue有回复、贡献者>30人、PR基本及时处理 |
| 5-6 | Issue偶尔有回复、贡献者>10人、PR处理较慢 |
| 3-4 | Issue长期无回复、贡献者<10人、PR积压严重 |
| 1-2 | 几乎无社区活动、贡献者<5人 |
| 0 | 项目已废弃或无社区 |

判断依据：
- Issue数量和最近回复时间
- PR数量和合并时间
- 贡献者数量（contributors）
- 最近30天的提交频率
- 是否有CONTRIBUTING.md

### 3. update_frequency（更新频率）

评估项目的维护活跃度、版本发布节奏。

| 分数 | 标准 |
|------|------|
| 9-10 | 每周有提交、每月发布版本、有明确的发布计划 |
| 7-8 | 每周有提交、季度发布版本 |
| 5-6 | 每月有提交、有版本发布但不规律 |
| 3-4 | 每季度有提交、很少发布版本 |
| 1-2 | 超过6个月无更新 |
| 0 | 超过1年无更新或已废弃 |

判断依据：
- 最近提交日期（updated_at）
- 提交频率统计
- Release版本数量和最近发布日期
- 是否有CHANGELOG.md

### 4. documentation（文档完整性）

评估项目的文档质量、可用性、完整性。

| 分数 | 标准 |
|------|------|
| 9-10 | README完整（含安装、使用、示例）、有API文档、有使用指南、有FAQ、有变更日志 |
| 7-8 | README完整、有基本API文档、有部分示例 |
| 5-6 | README基本完整、有简单说明 |
| 3-4 | README简陋、缺少关键信息 |
| 1-2 | README只有标题或非常简单 |
| 0 | 无README或无法理解 |

判断依据：
- README.md长度和内容完整性
- 是否有docs/目录
- 是否有API文档（Swagger/OpenAPI）
- 是否有示例代码（examples/）
- 是否有CHANGELOG.md
- 是否有CONTRIBUTING.md

### 5. security（安全状况）

评估项目的安全性、漏洞管理、依赖安全。

| 分数 | 标准 |
|------|------|
| 9-10 | 无已知高危漏洞、依赖安全、有安全策略（SECURITY.md）、及时修复漏洞 |
| 7-8 | 无高危漏洞、依赖基本安全、有基本的安全措施 |
| 5-6 | 有已知漏洞但已修复、依赖安全性一般 |
| 3-4 | 有未修复的中危漏洞、依赖有安全问题 |
| 1-2 | 有高危漏洞未修复、依赖不安全 |
| 0 | 存在严重安全问题或无法评估 |

判断依据：
- 是否有SECURITY.md
- 依赖文件（package.json、requirements.txt）中的已知漏洞
- 是否有Dependabot/Renovate配置
- 许可证类型（MIT、Apache等）
- 最近的安全更新

### 6. community_impact（社区影响力）

评估项目的Star、Fork、引用情况、行业认可度。

| 分数 | 标准 |
|------|------|
| 9-10 | Star>10000、Fork>1000、被知名项目引用、有行业影响力 |
| 7-8 | Star>5000、Fork>500、有一定影响力 |
| 5-6 | Star>1000、Fork>100、在特定领域有影响 |
| 3-4 | Star>100、Fork>10、小众但有用 |
| 1-2 | Star<100、影响力有限 |
| 0 | 几乎无关注 |

判断依据：
- Star数量
- Fork数量
- Watch数量
- 是否被其他知名项目依赖
- 是否有相关论文或文章引用
- 是否有徽章（badges）显示使用情况

## 输出要求

你应该：
- 基于输入数据客观评分，严格按上述标准执行
- 请给出大致评分即可，不必过度纠察细节
- detail字段给出具体中文依据，引用输入数据中的事实
- summary字段给出项目整体总结，包含主要优势和待改进方面

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
    })
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
    }, stream=True)
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
