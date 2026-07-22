---
feature: adapt-structured-input
status: delivered
specs: []
plans:
  - docs/compose/plans/2026-07-22-adapt-structured-input.md
branch: feature/analyze
commits: 97a092d..b4546b5
---

# 适配结构化输入 — Final Report

## What Was Built

本次实现为分析模块添加了对 data/get 分支结构化 JSON 数据的支持。系统现在能够自动检测输入文件格式（纯文本 .txt 或结构化 JSON .json），并透明地将 JSON 数据转换为文本格式供 LLM 分析。这一改动保持了完全的向后兼容性，现有的纯文本输入方式不受影响。

核心功能包括：
- 新增 JSON 到文本转换器，将 RepoReport 结构化数据转换为可读文本
- 修改文件处理器，自动检测输入格式并选择正确的处理流程
- 扩展命令行接口，支持 `--input-format` 参数
- 提供完整的示例文件和更新的文档

## Architecture

### 组件结构

```
输入层
├── file_handler.py (修改)
│   ├── read_input_file() - 自动检测格式
│   └── write_output_file() - 输出 JSON
├── json_to_text.py (新增)
│   └── convert_json_to_text() - JSON 转文本
└── analyze.py (修改)
    └── argparse 命令行参数
```

### 数据流

```
.txt 文件 → read_input_file() → 纯文本 → analyze_github_project()
.json 文件 → read_input_file() → convert_json_to_text() → 纯文本 → analyze_github_project()
```

### 关键接口

**convert_json_to_text(data: Dict[str, Any]) -> str**
- 输入：RepoReport 格式的 JSON 字典
- 输出：格式化的纯文本字符串
- 包含：仓库信息、语言分布、提交活跃度、Issue/PR 统计、贡献者画像、文档质量、发布信息

**read_input_file(file_path: str) -> Optional[str]**
- 自动检测文件扩展名
- .json 文件：尝试解析为 RepoReport 格式并转换
- .txt 文件：直接返回内容
- 错误处理：JSON 解析失败时回退到纯文本

## Usage

### 命令行使用

```bash
# 纯文本输入（原有方式）
python analyze.py examples/sample_input.txt output.json

# JSON 输入（新增支持）
python analyze.py examples/sample_input.json output.json

# 批量分析（支持混合格式）
python batch_analyze.py examples/ output_dir/

# 指定输入格式（可选）
python analyze.py --input-format json input.json output.json
```

### JSON 输入格式

支持 data/get 分支返回的 RepoReport 结构：

```json
{
  "repo": {
    "full_name": "ggerganov/llama.cpp",
    "name": "llama.cpp",
    "stars": 80000,
    "forks": 12000,
    ...
  },
  "languages": {...},
  "commits": {...},
  "issues": {...},
  "pulls": {...},
  "contributors": {...},
  "docs": {...},
  "releases": {...}
}
```

### 自动转换

系统会自动将 JSON 数据转换为以下文本格式：

```
项目名称: llama.cpp
GitHub地址: https://github.com/ggerganov/llama.cpp
Star数: 80000
Fork数: 12000
主要语言: C++
许可证: MIT

语言分布:
  - C++: 60.0%
  - C: 30.0%
  - Python: 10.0%

提交活跃度:
  近30天提交: 100
  近90天提交: 300
  每周平均: 25.0
  最近提交: 2024-01-15
...
```

## Verification

### 测试覆盖

所有测试通过（10/10）：

| 测试文件 | 测试用例 | 状态 |
|----------|----------|------|
| test_json_to_text.py | test_convert_basic_structure | ✓ |
| test_json_to_text.py | test_convert_empty_json | ✓ |
| test_file_handler.py | test_read_txt_file | ✓ |
| test_file_handler.py | test_read_json_file | ✓ |
| test_cli.py | test_analyze_help | ✓ |
| test_analyze.py | test_main_with_valid_input | ✓ |
| test_analyzer.py | test_analyze_github_project_with_valid_input | ✓ |
| test_validators.py | test_valid_analysis_result | ✓ |
| test_validators.py | test_invalid_missing_status | ✓ |
| test_validators.py | test_invalid_score_range | ✓ |

### 手动测试

- 纯文本输入：✓ 正常工作
- JSON 输入：✓ 正常工作（自动转换）
- 批量分析：✓ 正常工作
- 错误处理：✓ LLM 服务器未运行时返回错误信息

### 边界情况

- 空 JSON：返回 "无有效数据"
- 无效 JSON：回退到纯文本处理
- 非 RepoReport 格式 JSON：作为普通文本处理

## Journey Log

- [lesson] JSON 到文本转换需要保持与原有纯文本格式的一致性，以便 LLM 能够正确理解
- [pivot] 最初计划添加 `--input-format` 参数，但发现自动检测更符合用户习惯，最终同时支持两种方式
- [lesson] Windows 环境下的编码问题需要特别注意，测试中使用字节串比较避免编码错误

## Source Materials

| File | Role | Notes |
|------|------|-------|
| docs/compose/plans/2026-07-22-adapt-structured-input.md | 实现计划 | 完整的任务分解和步骤 |
| src/json_to_text.py | 新增模块 | JSON 到文本转换器 |
| src/file_handler.py | 修改模块 | 自动格式检测 |
| analyze.py | 修改模块 | 命令行参数支持 |
| examples/sample_input.json | 新增示例 | JSON 输入格式示例 |
| SETUP.md | 更新文档 | 添加 JSON 输入说明 |
