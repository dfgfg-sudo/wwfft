"""
#!/bin/bash

# 企业工作流智能编排系统一键部署脚本
# 版本: 3.0.0

set -e

echo "🚀 开始部署企业工作流智能编排系统..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建目录结构
echo "📁 创建目录结构..."
mkdir -p ./config
mkdir -p ./data/postgres
mkdir -p ./data/redis
mkdir -p ./data/mongodb
mkdir -p ./logs
mkdir -p ./certs

# 复制配置文件
echo "📋 复制配置文件..."
cp plugin.json ./config/
cp openapi.yaml ./config/

# 生成Docker Compose配置
echo "🐳 生成Docker Compose配置..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: ewio-postgres
    environment:
      POSTGRES_DB: ewio_db
      POSTGRES_USER: ewio_user
      POSTGRES_PASSWORD: ewio_password_123
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ewio-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ewio_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ewio-redis
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    networks:
      - ewio-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:6
    container_name: ewio-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: ewio_admin
      MONGO_INITDB_ROOT_PASSWORD: ewio_admin_123
    volumes:
      - ./data/mongodb:/data/db
    ports:
      - "27017:27017"
    networks:
      - ewio-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  workflow-service:
    image: enterprise-workflow/workflow-service:3.0.0
    container_name: ewio-workflow-service
    environment:
      SPRING_PROFILES_ACTIVE: production
      DB_URL: jdbc:postgresql://postgres:5432/ewio_db
      DB_USERNAME: ewio_user
      DB_PASSWORD: ewio_password_123
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ewio-network

  ai-service:
    image: enterprise-workflow/ai-service:3.0.0
    container_name: ewio-ai-service
    environment:
      SPRING_PROFILES_ACTIVE: production
      MONGO_URI: mongodb://ewio_admin:ewio_admin_123@mongodb:27017/ewio_ai_db
      REDIS_HOST: redis
      REDIS_PORT: 6379
    ports:
      - "8081:8080"
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - ewio-network

  repair-service:
    image: enterprise-workflow/repair-service:3.0.0
    container_name: ewio-repair-service
    environment:
      SPRING_PROFILES_ACTIVE: production
      DB_URL: jdbc:postgresql://postgres:5432/ewio_db
      DB_USERNAME: ewio_user
      DB_PASSWORD: ewio_password_123
    ports:
      - "8082:8080"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ewio-network

  monitoring:
    image: grafana/grafana:latest
    container_name: ewio-monitoring
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - ./config/grafana:/etc/grafana
      - ./data/grafana:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - ewio-network

networks:
  ewio-network:
    driver: bridge
EOF

# 启动服务
echo "🚀 启动所有服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 测试API端点
echo "🧪 测试API端点..."
curl -X GET "http://localhost/v1/health" || true

echo "✅ 部署完成！"
echo "📊 监控面板: http://localhost:3000"
echo "🔧 API端点: http://localhost/v1/execute"
echo "📚 API文档: http://localhost/v1/openapi.yaml"
"""
