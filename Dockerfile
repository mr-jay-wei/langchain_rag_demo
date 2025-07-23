# RAG 系统 Docker 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY rag/ ./rag/
COPY app.py start_server.py ./
COPY .env* ./

# 创建必要的目录
RUN mkdir -p data local_models my_chromadb_vector_store

# 安装 Python 依赖
RUN uv sync --frozen

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["uv", "run", "python", "start_server.py", "--mode", "prod", "--host", "0.0.0.0", "--port", "8000"]