# 开发环境配置

本文档介绍如何配置本项目的本地开发环境。

## 1. 软件要求

请提前安装以下软件：

| 软件 | 建议版本 |
|------|----------|
| Python | 3.8 及以上 |
| Git | 最新版本 |
| llama.cpp | 支持 llama-server 的版本 |

---

## 2. 克隆项目

```bash
git clone https://github.com/BISTU-OSSD/team--17.git
cd team--17
```

---

## 3. 安装 Python 依赖

```bash
pip install -r requirements_main.txt
```

---

## 4. 配置环境变量

复制项目根目录中的 `.env.example` 文件，并重命名为 `.env`。

根据本机实际路径修改以下内容：

```text
LLAMA_SERVER=D:\20260721\llama-cpp\llama-server.exe
MODEL_PATH=D:\20260721\llama-cpp\Qwen3.5-9B-Q4_K_M.gguf
HOST=127.0.0.1
PORT=8080
```

---

## 5. 下载模型

由于模型文件体积较大（约 5.8GB），无法上传到 GitHub。

请根据项目 Issue 中提供的下载方式获取模型文件，并放置到配置文件指定的位置。

---

## 6. 启动项目

```bash
python run.py
```

程序启动成功后，会自动启动 llama.cpp 服务，并进入分析流程。

---

## 常见问题

### 找不到模型文件

请检查：

- `.env` 中 `MODEL_PATH` 是否正确
- 模型文件是否存在

---

### llama-server 无法启动

请检查：

- `LLAMA_SERVER` 是否填写正确
- 是否下载了完整的 llama.cpp

---

### Python 依赖安装失败

建议升级 pip：

```bash
python -m pip install --upgrade pip
```