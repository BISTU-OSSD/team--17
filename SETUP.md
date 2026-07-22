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