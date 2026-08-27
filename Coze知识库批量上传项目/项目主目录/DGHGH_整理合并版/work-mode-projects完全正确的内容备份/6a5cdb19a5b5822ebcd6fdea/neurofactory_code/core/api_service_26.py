# 构建镜像
docker build -t unified-automation .

# 运行容器
docker run -p 3000:3000 --env-file .env unified-automation

# 使用预构建镜像
docker pull unified-automation/center:latest
docker run -d -p 8080:8080 -e API_KEY=your_key unified-automation/center