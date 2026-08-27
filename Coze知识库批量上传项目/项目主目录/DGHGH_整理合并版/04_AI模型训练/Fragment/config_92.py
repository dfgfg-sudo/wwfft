"""
curl -X POST https://api.enterprise-workflow.com/v1/execute \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "operation_type": "process_luoyang_heritage",
    "operation_config": {
      "heritage_config": {
        "heritage_type": "intangible",
        "heritage_category": "traditional_craft",
        "action_type": "preserve",
        "processing_mode": "digital_preservation"
      }
    }
  }'
"""
