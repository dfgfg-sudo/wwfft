"""
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 复制需求文件并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 设置环境变量（需在运行时覆盖）
ENV VAULT_ADDR="https://vault.example.com"
ENV VAULT_TOKEN=""
ENV OPENCLAW_API_KEY=""

# 暴露端口（如有 Web 界面）
EXPOSE 8080

# 启动命令
CMD ["python", "main.py"]
"""
