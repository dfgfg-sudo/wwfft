"""
curl -X POST "https://api.quanchangjing.com/v1/operations/execute" \\
  -H "Authorization: Bearer your_jwt_token" \\
  -H "Content-Type: application/json" \\
  -d '{
    "operation_mode": "industry_analysis",
    "input_data": {"industry": "人工智能"},
    "analysis_type": "market_trends",
    "automation_enabled": true,
    "automation_level": "full"
  }'
"""
