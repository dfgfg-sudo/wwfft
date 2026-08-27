curl -X POST https://api.aiworkflowplatform.com/v1/operations/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_mode": "ai_enhancement",
    "input_data": {
      "data_type": "text",
      "enhancement_type": "semantic_enrichment",
      "input_text": "需要增强的文本内容",
      "quality_threshold": 0.9
    }
  }'