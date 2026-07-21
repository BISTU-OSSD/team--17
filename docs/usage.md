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