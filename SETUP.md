# 环境配置指南

## 1. Python环境

需要 Python 3.8 或更高版本。

```bash
python --version
```

## 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 3. 下载 llama.cpp

下载地址：https://github.com/ggerganov/llama.cpp/releases

选择 Windows 版本（如 `llama-b*-bin-win-cuda-*.zip`），解压到项目根目录的 `llama-cpp/` 文件夹。

需要的文件：
- `llama-server.exe`
- `llama.dll`
- `ggml-cuda.dll`
- 其他 dll 文件

## 4. 下载模型文件

下载 Qwen3.5-9B-Q4_K_M.gguf（约5GB），放到 `llama-cpp/` 目录。

可从 HuggingFace 搜索下载：
```
Qwen3.5-9B-Q4_K_M.gguf
```

## 5. 验证配置

```bash
# 检查文件是否齐全
ls llama-cpp/llama-server.exe
ls llama-cpp/Qwen3.5-9B-Q4_K_M.gguf

# 运行测试
python run.py examples/sample_input.txt test.json
```

## 目录结构

```
项目目录/
├── llama-cpp/
│   ├── llama-server.exe      # llama.cpp服务器
│   ├── *.dll                 # 动态链接库
│   └── Qwen3.5-9B-Q4_K_M.gguf  # 模型文件
├── analyze.py
├── batch_analyze.py
├── run.py
└── ...
```