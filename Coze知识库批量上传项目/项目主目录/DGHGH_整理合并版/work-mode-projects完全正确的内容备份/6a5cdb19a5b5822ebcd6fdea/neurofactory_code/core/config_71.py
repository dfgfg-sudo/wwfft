# 原始Docker Compose配置完全保留
version: '3.8'

services:
  coze-api:
    image: coze/automation-api:10.1.0
    container_name: coze-automation-api
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - COZE_API_KEY=${COZE_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/system/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  coze-worker:
    image: coze/automation-worker:10.1.0
    container_name: coze-automation-worker
    environment:
      - NODE_ENV=production
      - REDIS_URL=${REDIS_URL}
      - COZE_API_KEY=${COZE_API_KEY}
    volumes:
      - ./worker-logs:/app/logs
    depends_on:
      - coze-api
    deploy:
      replicas: 3

  redis:
    image: redis:7-alpine
    container_name: coze-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  postgres:
    image: postgres:15-alpine
    container_name: coze-postgres
    environment:
      - POSTGRES_DB=coze_automation
      - POSTGRES_USER=coze
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  redis-data:
  postgres-data: