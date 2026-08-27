# 构建镜像
docker build -t neurofactory-fusion:v8.0 .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -v ./data:/app/data \
  -v ./models:/app/models \
  --name neurofactory-fusion \
  neurofactory-fusion:v8.0