#!/bin/bash

# 企业工作流智能编排系统自动测试脚本

echo "🧪 开始自动化测试..."

# 测试健康检查
echo "1. 测试健康检查端点..."
curl -X GET "http://localhost/v1/health" \
  -H "Content-Type: application/json" \
  -w "\n状态码: %{http_code}\n"

# 测试工作流生成
echo "2. 测试工作流生成功能..."
curl -X POST "http://localhost/v1/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "operation_type": "generate_workflow",
    "operation_config": {
      "workflow_config": {
        "requirement_description": "测试电商订单处理流程",
        "business_domain": "ecommerce",
        "complexity_level": "simple",
        "validation_strictness": "standard"
      }
    },
    "version": "v1.0",
    "async_execution": false
  }' \
  -w "\n状态码: %{http_code}\n"

# 测试AI数据增强
echo "3. 测试AI数据增强功能..."
curl -X POST "http://localhost/v1/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "operation_type": "ai_enhancement",
    "operation_config": {
      "ai_enhancement_config": {
        "input_data": "测试数据清洗和增强",
        "enhancement_type": "cleaning",
        "output_format": "json"
      }
    },
    "version": "v1.0",
    "async_execution": false
  }' \
  -w "\n状态码: %{http_code}\n"

# 测试参数验证
echo "4. 测试参数验证功能..."
curl -X POST "http://localhost/v1/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "operation_type": "activate_emergency",
    "operation_config": {
      "emergency_config": {
        "emergency_level": "urgent",
        "activation_reason": "测试紧急情况"
      }
    }
  }' \
  -w "\n状态码: %{http_code}\n"

echo "✅ 自动化测试完成！"