# 项目部署说明

本文档介绍 DevSkillMapper 的部署流程。

## 项目结构

```
DevSkillMapper
│
├── src/                 # 核心源码
├── docs/                # 项目文档
├── tests/               # 单元测试
├── examples/            # 示例输入文件
│
├── analyze.py           # 单文件分析程序
├── batch_analyze.py     # 批量分析程序
├── run.py               # 项目启动入口
├── config.py            # 配置管理
├── llama_chat.py        # LLM 接口
├── llama_stream.py      # 流式输出
│
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
└── .gitignore
```

---

## 本地部署

### 第一步

安装 Python 依赖：

```bash
pip install -r requirements.txt
```

### 第二步

下载并部署 llama.cpp。

### 第三步

下载 GGUF 模型文件。

### 第四步

修改 `.env`：

```text
LLAMA_SERVER=...
MODEL_PATH=...
```

### 第五步

启动：

```bash
python run.py
```

---

## 后续部署计划

本项目计划采用前后端分离部署。

### 前端

部署平台：

- Vercel

负责内容：

- 页面展示
- 图表展示
- 调用后端接口

---

### 后端

部署平台：

- Railway

负责内容：

- GitHub 数据分析
- LLM 推理接口
- JSON 数据返回

---

### 持续集成

项目计划使用 GitHub Actions 实现：

- 自动安装依赖
- 自动检查 Python 代码语法
- 自动运行测试

---

## 注意事项

由于 GGUF 模型文件超过 GitHub 文件大小限制，因此模型文件不会上传到仓库。

开发者需要自行下载模型，并按照 `environment.md` 完成配置。

---

## 更新日志

| 日期 | 内容 |
|------|------|
| 2026-07-22 | 新增部署文档 |