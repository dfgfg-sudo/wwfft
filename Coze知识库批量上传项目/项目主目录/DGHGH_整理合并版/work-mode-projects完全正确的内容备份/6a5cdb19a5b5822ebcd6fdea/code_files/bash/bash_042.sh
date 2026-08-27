# 自动化处理
curl -X POST https://api.coze.com/v1/omnipotent-automation \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "operation_mode": "generate_workflow",
    "config": {
      "user_request": "创建零售业库存管理流程"
    }
  }'