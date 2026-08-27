curl -X POST https://api.coze.com/v1/repair/execute \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "operationMode": "auto_repair",
    "errorContext": {
      "errorCode": "101006",
      "source": "workflow_canvas"
    }
  }'