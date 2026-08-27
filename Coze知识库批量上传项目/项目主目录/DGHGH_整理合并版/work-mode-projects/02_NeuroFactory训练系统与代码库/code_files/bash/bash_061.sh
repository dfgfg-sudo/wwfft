# 构建镜像
docker build -t neuroforge-model .

# 运行容器
docker run -p 8000:8000 neuroforge-model

# 或使用 docker-compose
docker-compose up -d