# services/asr/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装 ffmpeg 和其它依赖
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . /app/

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8181"]
