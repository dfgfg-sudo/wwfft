# API Key认证
curl -X POST "https://api.unified-automation.com/v15/complete-automation?user_input=修复所有问题&repair_depth=comprehensive" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_input": "请修复所有Coze插件错误和工作流连接问题",
    "repair_depth": "comprehensive",
    "enable_automation": true
  }'

# Bearer Token认证
curl -X POST "https://api.unified-automation.com/v15/complete-automation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "user_input": "请修复工作流中的参数配置错误",
    "repair_depth": "thorough"
  }'

# 双重认证
curl -X POST "https://api.unified-automation.com/v15/complete-automation" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "user_input": "全面修复所有Coze插件和工作流问题",
    "repair_depth": "thorough",
    "include_testing": true
  }'