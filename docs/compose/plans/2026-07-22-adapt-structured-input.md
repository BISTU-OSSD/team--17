# 适配结构化输入实现计划

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/adapt-structured-input.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修改分析模块，支持接收 data/get 分支的结构化 JSON 数据作为输入，同时保持向后兼容纯文本输入

**Architecture:** 
1. 新增 JSON 输入转换器，将结构化数据转为文本格式
2. 修改文件处理器，自动识别输入格式（纯文本 vs JSON）
3. 保持现有命令行接口不变，透明支持新格式

**Tech Stack:** Python, Pydantic (数据模型), requests (HTTP 调用)

---

## 任务分解

### Task 1: 创建 JSON 到文本的转换器

**Covers:** 支持结构化数据输入

**Files:**
- Create: `src/json_to_text.py`
- Test: `tests/test_json_to_text.py`

**Interfaces:**
- Consumes: RepoReport JSON 字典
- Produces: 格式化的纯文本字符串（与现有 txt 输入格式一致）

**步骤:**

- [ ] **Step 1: 创建测试文件**

```python
# tests/test_json_to_text.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from json_to_text import convert_json_to_text

def test_convert_basic_structure():
    """测试基本结构转换"""
    sample_json = {
        "repo": {
            "full_name": "facebook/react",
            "description": "A JavaScript library",
            "language": "JavaScript",
            "stars": 220000,
            "forks": 45000,
            "license": "MIT"
        },
        "commits": {
            "commits_last_30_days": 50
        },
        "issues": {
            "total_open": 1000
        },
        "contributors": {
            "total_contributors": 1500
        }
    }
    
    result = convert_json_to_text(sample_json)
    
    assert "facebook/react" in result
    assert "JavaScript" in result
    assert "220000" in result
    assert "Star" in result or "stars" in result.lower()

def test_convert_empty_json():
    """测试空 JSON 处理"""
    result = convert_json_to_text({})
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_json_to_text.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: 实现转换器**

```python
# src/json_to_text.py
"""JSON 结构化数据到文本格式的转换器"""

from typing import Dict, Any


def convert_json_to_text(data: Dict[str, Any]) -> str:
    """
    将 RepoReport JSON 转换为纯文本格式
    
    Args:
        data: RepoReport 结构化数据字典
        
    Returns:
        格式化的纯文本字符串
    """
    lines = []
    
    # 仓库基本信息
    repo = data.get("repo", {})
    if repo:
        lines.append(f"项目名称: {repo.get('name', '未知')}")
        lines.append(f"GitHub地址: https://github.com/{repo.get('full_name', '')}")
        lines.append(f"项目描述: {repo.get('description', '无')}")
        lines.append(f"主要语言: {repo.get('language', '未知')}")
        lines.append(f"Star数: {repo.get('stars', 0)}")
        lines.append(f"Fork数: {repo.get('forks', 0)}")
        lines.append(f"许可证: {repo.get('license', '未知')}")
        lines.append(f"Open Issues: {repo.get('open_issues_count', 0)}")
        lines.append("")
    
    # 语言分布
    languages = data.get("languages", {})
    if languages and languages.get("languages"):
        lines.append("语言分布:")
        for lang in languages["languages"][:5]:  # 只显示前5种
            lines.append(f"  - {lang.get('language')}: {lang.get('percentage', 0):.1f}%")
        lines.append("")
    
    # Commit 活跃度
    commits = data.get("commits", {})
    if commits:
        lines.append("提交活跃度:")
        lines.append(f"  近30天提交: {commits.get('commits_last_30_days', 0)}")
        lines.append(f"  近90天提交: {commits.get('commits_last_90_days', 0)}")
        lines.append(f"  每周平均: {commits.get('commit_frequency_per_week', 0)}")
        lines.append(f"  最近提交: {commits.get('last_commit_date', '未知')}")
        lines.append("")
    
    # Issue 统计
    issues = data.get("issues", {})
    if issues:
        lines.append("Issue 统计:")
        lines.append(f"  开放Issue数: {issues.get('total_open', 0)}")
        lines.append(f"  关闭率: {issues.get('close_rate', 0) * 100:.1f}%")
        avg_close = issues.get('avg_close_time_hours')
        if avg_close:
            lines.append(f"  平均关闭时长: {avg_close:.1f}小时")
        lines.append("")
    
    # PR 统计
    pulls = data.get("pulls", {})
    if pulls:
        lines.append("PR 统计:")
        lines.append(f"  已合并PR: {pulls.get('total_merged', 0)}")
        lines.append(f"  合并率: {pulls.get('merge_rate', 0) * 100:.1f}%")
        avg_merge = pulls.get('avg_merge_time_hours')
        if avg_merge:
            lines.append(f"  平均合并时长: {avg_merge:.1f}小时")
        lines.append("")
    
    # 贡献者画像
    contributors = data.get("contributors", {})
    if contributors:
        lines.append("贡献者信息:")
        lines.append(f"  总贡献者数: {contributors.get('total_contributors', 0)}")
        lines.append(f"  近30天活跃: {contributors.get('active_30d_contributors', 0)}")
        lines.append(f"  Bus Factor: {contributors.get('bus_factor', 0)}")
        lines.append("")
    
    # 文档质量
    docs = data.get("docs", {})
    if docs:
        lines.append("文档质量:")
        lines.append(f"  README: {'有' if docs.get('has_readme') else '无'}")
        lines.append(f"  CONTRIBUTING: {'有' if docs.get('has_contributing') else '无'}")
        lines.append(f"  LICENSE: {'有' if docs.get('has_license') else '无'}")
        lines.append(f"  CHANGELOG: {'有' if docs.get('has_changelog') else '无'}")
        lines.append("")
    
    # 发布信息
    releases = data.get("releases", {})
    if releases:
        lines.append("版本发布:")
        lines.append(f"  总发布数: {releases.get('total_releases', 0)}")
        lines.append(f"  最新版本: {releases.get('latest_release_tag', '未知')}")
        lines.append(f"  最新发布日期: {releases.get('latest_release_date', '未知')}")
        lines.append("")
    
    return "\n".join(lines)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_json_to_text.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add src/json_to_text.py tests/test_json_to_text.py
git commit -m "feat: add JSON to text converter for structured input"
```

---

### Task 2: 修改文件处理器支持自动格式检测

**Covers:** 自动识别输入格式

**Files:**
- Modify: `src/file_handler.py`
- Test: `tests/test_file_handler.py`

**Interfaces:**
- Consumes: 文件路径（.txt 或 .json）
- Produces: 统一的文本内容字符串

**步骤:**

- [ ] **Step 1: 创建测试文件**

```python
# tests/test_file_handler.py
import sys
import os
import tempfile
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from file_handler import read_input_file

def test_read_txt_file():
    """测试读取纯文本文件"""
    content = "项目名称: test\nGitHub地址: https://github.com/test/repo"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = read_input_file(temp_path)
        assert result == content
    finally:
        os.unlink(temp_path)

def test_read_json_file():
    """测试读取 JSON 文件"""
    json_data = {
        "repo": {
            "full_name": "test/repo",
            "name": "repo",
            "stars": 100
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(json_data, f)
        temp_path = f.name
    
    try:
        result = read_input_file(temp_path)
        assert isinstance(result, str)
        assert "test/repo" in result
        assert "100" in result
    finally:
        os.unlink(temp_path)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_file_handler.py::test_read_json_file -v`
Expected: FAIL (JSON 文件被当作纯文本读取)

- [ ] **Step 3: 修改文件处理器**

```python
# src/file_handler.py
"""文件读写工具"""

import json
import os
import sys

sys.path.append(os.path.dirname(__file__))
from json_to_text import convert_json_to_text


def read_input_file(file_path: str) -> str | None:
    """
    读取输入文件，自动检测格式
    
    Args:
        file_path: 文件路径（支持 .txt 和 .json）
        
    Returns:
        文本内容，失败返回 None
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检测是否为 JSON 文件
        if file_path.lower().endswith('.json'):
            try:
                json_data = json.loads(content)
                # 如果是 RepoReport 格式，转换为文本
                if isinstance(json_data, dict) and ('repo' in json_data or 'languages' in json_data):
                    return convert_json_to_text(json_data)
                # 否则作为普通文本返回
                return content
            except json.JSONDecodeError:
                # JSON 解析失败，作为普通文本返回
                return content
        
        # 非 JSON 文件，直接返回文本
        return content
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


def write_output_file(data: dict, output_path: str) -> bool:
    """
    写入输出文件
    
    Args:
        data: 要写入的数据
        output_path: 输出文件路径
        
    Returns:
        是否成功
    """
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_file_handler.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add src/file_handler.py tests/test_file_handler.py
git commit -m "feat: auto-detect input format (txt or json)"
```

---

### Task 3: 添加命令行参数支持 JSON 输入

**Covers:** 命令行接口扩展

**Files:**
- Modify: `analyze.py`
- Modify: `batch_analyze.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: 命令行参数（--input-format json 或 auto）
- Produces: 自动选择正确的处理流程

**步骤:**

- [ ] **Step 1: 创建测试文件**

```python
# tests/test_cli.py
import sys
import os
import subprocess
sys.path.append(os.path.dirname(__file__))

def test_analyze_help():
    """测试分析工具帮助信息"""
    result = subprocess.run(
        [sys.executable, 'analyze.py', '--help'],
        capture_output=True,
        text=True,
        cwd=os.path.join(os.path.dirname(__file__), '..')
    )
    assert result.returncode == 0
    assert 'input_file' in result.stdout
```

- [ ] **Step 2: 运行测试验证通过**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (帮助信息应该已存在)

- [ ] **Step 3: 修改 analyze.py**

```python
# analyze.py (修改后)
import sys
import os
import argparse

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import analyze_github_project
from file_handler import read_input_file, write_output_file
from validators import validate_analysis_result

def main():
    parser = argparse.ArgumentParser(description='GitHub项目分析工具')
    parser.add_argument('input_file', help='上游输入文件路径（支持 .txt 或 .json）')
    parser.add_argument('output_file', help='输出JSON文件路径')
    parser.add_argument('--input-format', choices=['auto', 'txt', 'json'], 
                       default='auto', help='输入格式（默认自动检测）')
    
    args = parser.parse_args()
    
    print(f"开始分析项目...")
    print(f"输入文件: {args.input_file}")
    print(f"输出文件: {args.output_file}")
    print(f"输入格式: {args.input_format}")
    
    # 读取输入文件
    text_content = read_input_file(args.input_file)
    if text_content is None:
        print("错误: 无法读取输入文件")
        sys.exit(1)
    
    # 分析项目
    print("正在调用LLM进行分析...")
    result = analyze_github_project(text_content)
    
    # 验证结果
    if result.get("status") == "error":
        print(f"分析失败: {result.get('message', '未知错误')}")
        # 写入错误结果
        write_output_file(result, args.output_file)
        sys.exit(1)
    
    # 处理失败但结构完整的响应
    if result.get("status") == "failed":
        print(f"警告: {result.get('summary', '分析失败')}")
    
    # 验证输出格式
    if not validate_analysis_result(result):
        print("警告: 输出格式不符合标准，但仍然保存")
    
    # 写入输出文件
    if write_output_file(result, args.output_file):
        print("分析完成!")
        print(f"结果已保存到: {args.output_file}")
        print(f"项目总分: {result.get('total_score', 'N/A')}")
    else:
        print("错误: 无法写入输出文件")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
git add analyze.py tests/test_cli.py
git commit -m "feat: add input format detection to CLI"
```

---

### Task 4: 更新文档和示例

**Covers:** 文档更新

**Files:**
- Modify: `SETUP.md`
- Create: `examples/sample_input.json`

**步骤:**

- [ ] **Step 1: 创建 JSON 示例文件**

```json
// examples/sample_input.json
{
  "repo": {
    "full_name": "ggerganov/llama.cpp",
    "name": "llama.cpp",
    "description": "Port of Meta's LLaMA model in C/C++",
    "language": "C++",
    "topics": ["llm", "inference", "gpu"],
    "license": "MIT",
    "stars": 80000,
    "forks": 12000,
    "open_issues_count": 200,
    "created_at": "2023-03-13T00:00:00Z",
    "pushed_at": "2024-01-15T10:30:00Z"
  },
  "languages": {
    "total_bytes": 2000000,
    "languages": [
      {"language": "C++", "bytes": 1200000, "percentage": 60.0},
      {"language": "C", "bytes": 600000, "percentage": 30.0},
      {"language": "Python", "bytes": 200000, "percentage": 10.0}
    ]
  },
  "commits": {
    "commits_last_30_days": 100,
    "commits_last_90_days": 300,
    "commit_frequency_per_week": 25.0,
    "last_commit_date": "2024-01-15"
  },
  "issues": {
    "total_open": 200,
    "total_closed": 1500,
    "close_rate": 0.88,
    "avg_close_time_hours": 72.5,
    "recent_30d_opened": 30,
    "recent_30d_closed": 50
  },
  "pulls": {
    "total_open": 50,
    "total_closed": 800,
    "total_merged": 750,
    "merge_rate": 0.94,
    "avg_merge_time_hours": 48.0,
    "recent_30d_opened": 20,
    "recent_30d_merged": 40
  },
  "contributors": {
    "total_contributors": 500,
    "active_30d_contributors": 50,
    "top_contributors": [
      {"login": "ggerganov", "contributions": 5000, "avatar_url": ""},
      {"login": "user2", "contributions": 1000, "avatar_url": ""}
    ],
    "new_contributor_ratio": 0.15,
    "bus_factor": 3
  },
  "docs": {
    "has_readme": true,
    "readme_length": 8000,
    "has_license": true,
    "license_spdx": "MIT",
    "has_contributing": true,
    "has_code_of_conduct": true,
    "has_changelog": true
  },
  "releases": {
    "total_releases": 50,
    "latest_release_tag": "b2000",
    "latest_release_date": "2024-01-10",
    "release_frequency_6m": 8.0
  }
}
```

- [ ] **Step 2: 更新 SETUP.md**

```markdown
# 环境配置指南

## 1. Python环境

需要 Python 3.8 或更高版本。

```bash
python --version
```

## 2. 安装Python依赖

```bash
pip install requests pytest
```

## 3. 下载 llama.cpp

下载地址：https://github.com/ggerganov/llama.cpp/releases

1. 下载 Windows 版本（如 `llama-b*-bin-win-cuda-*.zip`）
2. 解压到项目根目录的 `llama-cpp/` 文件夹
3. 确保 `llama-cpp/` 目录下有以下文件：
   - `llama-server.exe`
   - `llama.dll`
   - `ggml-cuda.dll`
   - 其他 dll 文件

## 4. 下载模型文件

下载 `Qwen3.5-9B-Q4_K_M.gguf`（约5GB），放到 `llama-cpp/` 目录。

可在 HuggingFace 搜索：https://huggingface.co/models?search=Qwen3.5-9B-Q4_K_M

## 5. 验证配置

```bash
# 检查文件是否齐全
dir llama-cpp\llama-server.exe
dir llama-cpp\Qwen3.5-9B-Q4_K_M.gguf

# 运行测试
python run.py examples\sample_input.txt test.json
```

## 6. 支持的输入格式

### 纯文本格式 (.txt)

```
项目名称: llama.cpp
GitHub地址: https://github.com/ggerganov/llama.cpp
Star数: 80000
Fork数: 12000
主要语言: C++
```

### JSON 格式 (.json)

支持 data/get 分支返回的结构化数据格式，程序会自动转换为文本格式进行分析。

```bash
# 使用 JSON 输入
python analyze.py examples\sample_input.json output.json

# 使用纯文本输入
python analyze.py examples\sample_input.txt output.json
```

## 目录结构

```
项目目录/
├── llama-cpp/
│   ├── llama-server.exe          # llama.cpp服务器
│   ├── *.dll                     # 动态链接库
│   └── Qwen3.5-9B-Q4_K_M.gguf  # 模型文件
├── analyze.py                    # 单文件分析
├── batch_analyze.py              # 批量分析
├── run.py                        # 主入口（启动服务器+分析）
├── llama_chat.py                 # LLM调用接口
├── llama_stream.py               # 流式对话
├── src/                          # 源码模块
├── tests/                        # 测试文件
├── examples/                     # 示例文件
└── docs/                         # 文档
```

## 使用方式

```bash
# 单文件分析（纯文本）
python run.py examples\sample_input.txt output.json

# 单文件分析（JSON）
python run.py examples\sample_input.json output.json

# 批量分析
python run.py projects/ results/

# 交互对话
python run.py
```
```

- [ ] **Step 3: 提交代码**

```bash
git add examples/sample_input.json SETUP.md
git commit -m "docs: add JSON example and update setup guide"
```

---

## 验证清单

完成所有任务后，运行以下验证：

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 测试纯文本输入
python analyze.py examples/sample_input.txt test_output.json

# 3. 测试 JSON 输入
python analyze.py examples/sample_input.json test_json_output.json

# 4. 批量测试
python batch_analyze.py examples/ test_batch_output/
```

---

## 注意事项

1. **向后兼容**：现有纯文本输入方式完全保持不变
2. **自动检测**：程序会根据文件扩展名自动选择处理方式
3. **错误处理**：JSON 解析失败时会回退到纯文本处理
4. **性能**：转换器是轻量级的，不会影响分析性能
