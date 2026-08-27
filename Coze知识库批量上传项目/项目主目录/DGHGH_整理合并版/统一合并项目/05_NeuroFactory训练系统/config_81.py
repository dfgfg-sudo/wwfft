"""
# 紧急模式激活示例
curl -X POST https://api.enterprise-workflow.com/v1/execute \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "operation_type": "activate_emergency",
    "operation_config": {
      "emergency_config": {
        "emergency_level": "critical",
        "activation_reason": "系统检测到严重安全威胁",
        "auto_recovery": true,
        "recovery_strategy": "immediate"
      }
    }
  }'

# 工作流生成示例
curl -X POST https://api.enterprise-workflow.com/v1/execute \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "operation_type": "generate_workflow",
    "operation_config": {
      "workflow_config": {
        "requirement_description": "需要创建一个电商订单处理工作流，包含库存检查、支付验证和物流分配",
        "business_domain": "ecommerce",
        "complexity_level": "medium"
      }
    },
    "async_execution": true
  }'
"""
