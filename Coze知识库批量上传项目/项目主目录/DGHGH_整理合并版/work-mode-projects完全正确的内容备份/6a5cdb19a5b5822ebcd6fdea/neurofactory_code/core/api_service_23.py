# Coze全场景智能自动化超级中枢 - 完整使用指南

## 🚀 快速开始

### 1. 认证获取
```bash
curl -X POST https://api.coze.com/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }'