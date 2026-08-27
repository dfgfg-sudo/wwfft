# config.yaml - 主配置文件
workflow_automation:
  coze_api:
    base_url: "https://api.coze.cn"
    api_key: "${COZE_API_KEY}"
    workspace_id: "your_workspace_id"
    
  batch_processing:
    max_concurrent: 5
    retry_attempts: 3
    batch_size: 100
    incremental_field: "updated_at"
    
  templates:
    workflow_template_path: "./templates/workflow.json.j2"
    node_template_path: "./templates/nodes/"
    
  data_sources:
    - type: "database"
      connection: "${DB_CONNECTION}"
      query: "SELECT * FROM source_data WHERE updated_at > :last_run"
    - type: "api"
      endpoint: "https://api.example.com/data"
    - type: "file"
      path: "./data/incremental_*.json"