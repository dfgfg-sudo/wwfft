"""
curl -X POST https://api.coze.com/v1/workflows/generate \\
  -H "X-API-Key: your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "电商自动化流程",
    "description": "自动处理订单和库存的工作流",
    "industry": "零售业",
    "nodes": [
      {
        "type": "order_processing",
        "config": {"auto_confirm": true}
      }
    ]
  }'
"""
