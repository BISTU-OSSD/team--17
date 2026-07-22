# 下游接口实现计划

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/downstream-interface.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一个稳定的下游接口，将分析模块的JSON输出提供给前端使用。

**Architecture:** 分析模块读取上游纯文本文件，调用LLM进行GitHub项目评估，输出标准化JSON文件供下游前端读取。采用文件接口模式，简单可靠。

**Tech Stack:** Python, JSON Schema验证, 文件I/O

## Global Constraints

- Python 3.8+ 兼容性
- 使用现有的llama_chat.py和llama_stream.py中的LLM调用逻辑
- 输出必须符合定义的JSON格式
- 错误处理必须返回明确的错误码和消息

---

## 接口规范

### 输入格式（上游纯文本）

```markdown
项目名称: xxx
GitHub地址: https://github.com/org/repo
Star数: 12345
Fork数: 5678
主要语言: Python
许可证: MIT

README内容:
[这里放README原文]

最近Issue数量: 10
最近PR数量: 5
```

### 输出格式（下游JSON）

```json
{
  "status": "success",
  "analysis_id": "uuid",
  "repo_url": "https://github.com/org/repo",
  "scores": {
    "code_quality": {"score": 8.5, "detail": "..."},
    "community_activity": {"score": 7.0, "detail": "..."},
    "update_frequency": {"score": 9.0, "detail": "..."},
    "documentation": {"score": 6.5, "detail": "..."},
    "security": {"score": 8.0, "detail": "..."},
    "community_impact": {"score": 9.5, "detail": "..."}
  },
  "total_score": 8.1,
  "summary": "...",
  "timestamp": "2026-07-21T10:00:00Z"
}
```

---

### Task 1: 创建JSON验证模块

**Covers:** 输出格式验证

**Files:**
- Create: `src/validators.py`
- Test: `tests/test_validators.py`

**Interfaces:**
- Consumes: 无
- Produces: `validate_analysis_result(data: dict) -> bool`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from src.validators import validate_analysis_result

def test_valid_analysis_result():
    valid_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 8.5, "detail": "Good code quality"},
            "community_activity": {"score": 7.0, "detail": "Active community"},
            "update_frequency": {"score": 9.0, "detail": "Regular updates"},
            "documentation": {"score": 6.5, "detail": "Adequate docs"},
            "security": {"score": 8.0, "detail": "Secure"},
            "community_impact": {"score": 9.5, "detail": "High impact"}
        },
        "total_score": 8.1,
        "summary": "Overall good project",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    assert validate_analysis_result(valid_data) == True

def test_invalid_missing_status():
    invalid_data = {"repo_url": "https://github.com/test/repo"}
    assert validate_analysis_result(invalid_data) == False

def test_invalid_score_range():
    invalid_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 15.0, "detail": "Out of range"},  # 超过10分
            "community_activity": {"score": 7.0, "detail": "Good"},
            "update_frequency": {"score": 9.0, "detail": "Good"},
            "documentation": {"score": 6.5, "detail": "Good"},
            "security": {"score": 8.0, "detail": "Good"},
            "community_impact": {"score": 9.5, "detail": "Good"}
        },
        "total_score": 8.1,
        "summary": "Good",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    assert validate_analysis_result(invalid_data) == False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_validators.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.validators'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/validators.py
from typing import Dict, Any

def validate_analysis_result(data: Dict[str, Any]) -> bool:
    """验证分析结果是否符合标准格式"""
    required_fields = ["status", "analysis_id", "repo_url", "scores", "total_score", "summary", "timestamp"]
    
    # 检查必需字段
    for field in required_fields:
        if field not in data:
            return False
    
    # 验证status
    if data["status"] != "success":
        return False
    
    # 验证scores结构
    required_scores = ["code_quality", "community_activity", "update_frequency", 
                      "documentation", "security", "community_impact"]
    for score_name in required_scores:
        if score_name not in data["scores"]:
            return False
        score_data = data["scores"][score_name]
        if "score" not in score_data or "detail" not in score_data:
            return False
        # 验证分数范围
        if not (0 <= score_data["score"] <= 10):
            return False
    
    # 验证total_score
    if not (0 <= data["total_score"] <= 10):
        return False
    
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_validators.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/validators.py tests/test_validators.py
git commit -m "feat: add JSON validation for analysis results"
```

---

### Task 2: 创建分析模块接口

**Covers:** 分析模块输入输出接口

**Files:**
- Create: `src/analyzer.py`
- Modify: `llama_chat.py` (提取核心函数)
- Test: `tests/test_analyzer.py`

**Interfaces:**
- Consumes: 纯文本内容 (str)
- Produces: `analyze_github_project(text_content: str) -> Dict[str, Any]`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from src.analyzer import analyze_github_project

def test_analyze_github_project_with_valid_input():
    valid_input = """
项目名称: test-project
GitHub地址: https://github.com/test/repo
Star数: 1000
Fork数: 100
主要语言: Python
许可证: MIT

README内容:
这是一个测试项目，用于验证分析模块的功能。

最近Issue数量: 10
最近PR数量: 5
"""
    result = analyze_github_project(valid_input)
    
    # 验证返回结构
    assert "status" in result
    assert "analysis_id" in result
    assert "repo_url" in result
    assert "scores" in result
    assert "total_score" in result
    assert "summary" in result
    assert "timestamp" in result
    
    # 验证scores结构
    required_scores = ["code_quality", "community_activity", "update_frequency", 
                      "documentation", "security", "community_impact"]
    for score_name in required_scores:
        assert score_name in result["scores"]
        assert "score" in result["scores"][score_name]
        assert "detail" in result["scores"][score_name]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analyzer.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.analyzer'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/analyzer.py
import json
import uuid
from datetime import datetime
from typing import Dict, Any
import requests
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_chat import chat, SYSTEM_PROMPT, SERVER_URL, MODEL_PATH

def analyze_github_project(text_content: str) -> Dict[str, Any]:
    """
    分析GitHub项目，返回标准化JSON结果
    
    Args:
        text_content: 上游爬取的纯文本内容
        
    Returns:
        标准化的分析结果字典
    """
    try:
        # 调用LLM分析
        prompt = SYSTEM_PROMPT + "\n" + text_content
        raw_result = chat(prompt, "请评估以上GitHub项目")
        
        # 解析JSON结果
        try:
            analysis_result = json.loads(raw_result)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error_type": "JSON_PARSE_ERROR",
                "message": "LLM返回的不是有效JSON",
                "raw_response": raw_result
            }
        
        # 提取项目名称（从输入文本中）
        repo_url = ""
        for line in text_content.split("\n"):
            if "GitHub地址:" in line:
                repo_url = line.split("GitHub地址:")[1].strip()
                break
        
        # 构建标准化输出
        standardized_result = {
            "status": "success",
            "analysis_id": str(uuid.uuid4()),
            "repo_url": repo_url,
            "scores": {},
            "total_score": 0.0,
            "summary": "",
            "timestamp": datetime.now().isoformat()
        }
        
        # 转换分数格式
        score_mapping = {
            "代码质量": "code_quality",
            "社区活跃度": "community_activity", 
            "更新频率": "update_frequency",
            "文档完整性": "documentation",
            "安全状况": "security",
            "社区影响力": "community_impact"
        }
        
        total_score = 0.0
        score_count = 0
        
        for cn_name, en_name in score_mapping.items():
            if cn_name in analysis_result.get("评分", {}):
                score_data = analysis_result["评分"][cn_name]
                standardized_result["scores"][en_name] = {
                    "score": score_data.get("分数", 0),
                    "detail": score_data.get("说明", "")
                }
                total_score += score_data.get("分数", 0)
                score_count += 1
        
        # 计算平均分
        if score_count > 0:
            standardized_result["total_score"] = round(total_score / score_count, 1)
        
        # 提取总结建议
        standardized_result["summary"] = analysis_result.get("总结建议", "")
        
        return standardized_result
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": "ANALYSIS_ERROR",
            "message": str(e)
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/analyzer.py tests/test_analyzer.py
git commit -m "feat: add analysis module interface with JSON output"
```

---

### Task 3: 创建文件处理工具

**Covers:** 文件读写接口

**Files:**
- Create: `src/file_handler.py`
- Test: `tests/test_file_handler.py`

**Interfaces:**
- Consumes: 文件路径 (str)
- Produces: `read_input_file(file_path: str) -> str`, `write_output_file(data: dict, output_path: str) -> bool`

- [ ] **Step 1: Write the failing test**

```python
import pytest
import tempfile
import os
from src.file_handler import read_input_file, write_output_file

def test_read_input_file():
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("项目名称: test-project\nGitHub地址: https://github.com/test/repo")
        temp_path = f.name
    
    try:
        content = read_input_file(temp_path)
        assert "项目名称: test-project" in content
        assert "GitHub地址: https://github.com/test/repo" in content
    finally:
        os.unlink(temp_path)

def test_write_output_file():
    test_data = {
        "status": "success",
        "analysis_id": "test-123",
        "repo_url": "https://github.com/test/repo",
        "scores": {
            "code_quality": {"score": 8.5, "detail": "Good"}
        },
        "total_score": 8.5,
        "summary": "Good project",
        "timestamp": "2026-07-21T10:00:00Z"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        result = write_output_file(test_data, temp_path)
        assert result == True
        
        # 验证文件内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            import json
            saved_data = json.load(f)
            assert saved_data["status"] == "success"
            assert saved_data["analysis_id"] == "test-123"
    finally:
        os.unlink(temp_path)

def test_read_nonexistent_file():
    result = read_input_file("nonexistent.txt")
    assert result is None

def test_write_to_invalid_path():
    test_data = {"status": "success"}
    result = write_output_file(test_data, "/invalid/path/file.json")
    assert result == False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_file_handler.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.file_handler'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/file_handler.py
import json
import os
from typing import Optional

def read_input_file(file_path: str) -> Optional[str]:
    """
    读取上游输入文件
    
    Args:
        file_path: 输入文件路径
        
    Returns:
        文件内容，如果文件不存在则返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误: 文件不存在 {file_path}")
        return None
    except Exception as e:
        print(f"错误: 读取文件失败 {e}")
        return None

def write_output_file(data: dict, output_path: str) -> bool:
    """
    写入JSON输出文件
    
    Args:
        data: 要写入的数据
        output_path: 输出文件路径
        
    Returns:
        是否成功写入
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"成功写入文件: {output_path}")
        return True
    except Exception as e:
        print(f"错误: 写入文件失败 {e}")
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_file_handler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/file_handler.py tests/test_file_handler.py
git commit -m "feat: add file handling utilities for input/output"
```

---

### Task 4: 创建主入口脚本

**Covers:** 完整的分析流程

**Files:**
- Create: `analyze.py`
- Test: `tests/test_analyze.py`

**Interfaces:**
- Consumes: 命令行参数 (input_file, output_file)
- Produces: JSON文件

- [ ] **Step 1: Write the failing test**

```python
import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from analyze import main

def test_main_with_valid_input():
    # 创建临时输入文件
    input_content = """
项目名称: test-project
GitHub地址: https://github.com/test/repo
Star数: 1000
Fork数: 100
主要语言: Python
许可证: MIT

README内容:
这是一个测试项目。

最近Issue数量: 10
最近PR数量: 5
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(input_content)
        input_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = f.name
    
    try:
        # 模拟LLM调用
        mock_response = {
            "项目名称": "test-project",
            "评分": {
                "代码质量": {"分数": 8.5, "说明": "Good code"},
                "社区活跃度": {"分数": 7.0, "说明": "Active"},
                "更新频率": {"分数": 9.0, "说明": "Regular"},
                "文档完整性": {"分数": 6.5, "说明": "Adequate"},
                "安全状况": {"分数": 8.0, "说明": "Secure"},
                "社区影响力": {"分数": 9.5, "说明": "High impact"}
            },
            "总结建议": "Overall good project"
        }
        
        with patch('analyze.analyze_github_project') as mock_analyze:
            mock_analyze.return_value = {
                "status": "success",
                "analysis_id": "test-123",
                "repo_url": "https://github.com/test/repo",
                "scores": {
                    "code_quality": {"score": 8.5, "detail": "Good code"},
                    "community_activity": {"score": 7.0, "detail": "Active"},
                    "update_frequency": {"score": 9.0, "detail": "Regular"},
                    "documentation": {"score": 6.5, "detail": "Adequate"},
                    "security": {"score": 8.0, "detail": "Secure"},
                    "community_impact": {"score": 9.5, "detail": "High impact"}
                },
                "total_score": 8.1,
                "summary": "Overall good project",
                "timestamp": "2026-07-21T10:00:00Z"
            }
            
            # 运行主函数
            with patch('sys.argv', ['analyze.py', input_path, output_path]):
                main()
            
            # 验证输出文件
            assert os.path.exists(output_path)
            with open(output_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                assert result["status"] == "success"
                assert result["repo_url"] == "https://github.com/test/repo"
    finally:
        os.unlink(input_path)
        os.unlink(output_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_analyze.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'analyze'"

- [ ] **Step 3: Write minimal implementation**

```python
# analyze.py
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
    parser.add_argument('input_file', help='上游输入文件路径（纯文本）')
    parser.add_argument('output_file', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    print(f"开始分析项目...")
    print(f"输入文件: {args.input_file}")
    print(f"输出文件: {args.output_file}")
    
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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_analyze.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analyze.py tests/test_analyze.py
git commit -m "feat: add main analysis script with CLI interface"
```

---

### Task 5: 创建使用文档和示例

**Covers:** 使用文档

**Files:**
- Create: `docs/usage.md`
- Create: `examples/sample_input.txt`
- Create: `examples/sample_output.json`

- [ ] **Step 1: 创建示例输入文件**

```bash
mkdir -p examples
```

```python
# examples/sample_input.txt
项目名称: llama.cpp
GitHub地址: https://github.com/ggml-org/llama.cpp
Star数: 80000
Fork数: 12000
主要语言: C++
许可证: MIT

README内容:
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

最近Issue数量: 200
最近PR数量: 50
贡献者数量: 500
```

- [ ] **Step 2: 创建示例输出文件**

```python
# examples/sample_output.json
{
  "status": "success",
  "analysis_id": "example-uuid-123",
  "repo_url": "https://github.com/ggml-org/llama.cpp",
  "scores": {
    "code_quality": {
      "score": 9.0,
      "detail": "代码质量很高，架构设计合理，测试覆盖率良好"
    },
    "community_activity": {
      "score": 9.5,
      "detail": "社区非常活跃，Issue和PR数量多，响应速度快"
    },
    "update_frequency": {
      "score": 9.0,
      "detail": "更新频率高，版本发布节奏稳定"
    },
    "documentation": {
      "score": 8.0,
      "detail": "文档完善，有详细的README和使用指南"
    },
    "security": {
      "score": 8.5,
      "detail": "无高危漏洞，依赖安全性良好"
    },
    "community_impact": {
      "score": 9.5,
      "detail": "影响力大，Star数和Fork数都很高"
    }
  },
  "total_score": 8.9,
  "summary": "llama.cpp是一个非常优秀的开源项目，代码质量高，社区活跃，文档完善，安全性好，影响力大。建议继续保持当前的开发节奏和社区建设。",
  "timestamp": "2026-07-21T10:00:00Z"
}
```

- [ ] **Step 3: 创建使用文档**

```markdown
# GitHub项目分析工具使用指南

## 概述

这是一个基于LLM的GitHub项目评估工具，可以自动分析GitHub项目的各个方面并生成评分报告。

## 安装

确保已安装Python 3.8+和必要的依赖：

```bash
pip install requests
```

## 使用方法

### 基本用法

```bash
python analyze.py <输入文件> <输出文件>
```

### 示例

```bash
# 使用示例输入文件
python analyze.py examples/sample_input.txt examples/sample_output.json

# 查看结果
cat examples/sample_output.json
```

## 输入文件格式

输入文件是纯文本格式，包含GitHub项目的基本信息：

```markdown
项目名称: 项目名称
GitHub地址: https://github.com/owner/repo
Star数: 12345
Fork数: 5678
主要语言: Python
许可证: MIT

README内容:
[README原文]

最近Issue数量: 10
最近PR数量: 5
```

## 输出文件格式

输出是JSON格式，包含以下字段：

```json
{
  "status": "success",
  "analysis_id": "uuid",
  "repo_url": "https://github.com/owner/repo",
  "scores": {
    "code_quality": {"score": 8.5, "detail": "..."},
    "community_activity": {"score": 7.0, "detail": "..."},
    "update_frequency": {"score": 9.0, "detail": "..."},
    "documentation": {"score": 6.5, "detail": "..."},
    "security": {"score": 8.0, "detail": "..."},
    "community_impact": {"score": 9.5, "detail": "..."}
  },
  "total_score": 8.1,
  "summary": "...",
  "timestamp": "2026-07-21T10:00:00Z"
}
```

## 错误处理

如果分析失败，输出文件会包含错误信息：

```json
{
  "status": "error",
  "error_type": "ANALYSIS_ERROR",
  "message": "错误描述"
}
```

## 集成说明

### 上游集成

上游爬取模块只需要输出纯文本文件，格式如上所示。

### 下游集成

下游前端可以直接读取JSON文件，解析scores字段进行展示。

## 开发说明

### 运行测试

```bash
pytest tests/ -v
```

### 项目结构

```
├── analyze.py          # 主入口脚本
├── llama_chat.py       # LLM调用接口
├── src/
│   ├── analyzer.py     # 分析模块
│   ├── file_handler.py # 文件处理
│   └── validators.py   # 验证模块
├── tests/              # 测试文件
├── examples/           # 示例文件
└── docs/               # 文档
```
```

- [ ] **Step 4: 验证文档完整性**

检查所有文件是否创建成功：

```bash
ls -la docs/usage.md
ls -la examples/sample_input.txt
ls -la examples/sample_output.json
```

- [ ] **Step 5: Commit**

```bash
git add docs/usage.md examples/
git commit -m "docs: add usage documentation and examples"
```

---

## Self-Review

**1. Spec coverage:** 
- 下游接口规范 ✓ (Task 1, 2)
- 输入输出格式 ✓ (Task 1, 2, 3)
- 错误处理 ✓ (Task 1, 2)
- 文件处理 ✓ (Task 3)
- 使用文档 ✓ (Task 5)

**2. Placeholder scan:** 所有步骤都有具体代码和命令。

**3. Type consistency:** 
- `validate_analysis_result(data: Dict[str, Any]) -> bool` ✓
- `analyze_github_project(text_content: str) -> Dict[str, Any]` ✓
- `read_input_file(file_path: str) -> Optional[str]` ✓
- `write_output_file(data: dict, output_path: str) -> bool` ✓

所有类型和函数名在任务间保持一致。

---

## Execution Handoff

检查记忆中是否有保存的执行风格偏好。如果没有，我需要询问用户。</think><tool_call>
<function=memory>
<parameter=operation>search