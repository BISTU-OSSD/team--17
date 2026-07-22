# 1. 使用官方 Python 3.11 轻量镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 4. 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 复制项目代码
COPY . .

# 6. 暴露 8000 端口
EXPOSE 8000

# 7. 改用 python -m uvicorn 启动，防止找不到可执行路径
CMD ["python", "-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]