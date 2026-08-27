curl -X POST https://api.enterprise-workflow.com/v1/execute \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_type": "repair_all_nodes",
    "operation_config": {
      "repair_config": {
        "workflow_id": "wf_123456789",
        "repair_scope": "all"
      }
    }
  }'