"""
第三部分：API测试套件 - 完全保留原始测试用例

```yaml
# 原始测试套件内容完全保留，仅修复YAML语法
name: "Coze全场景API测试套件"
version: "1.0.0"
description: "完整的API功能测试套件"

environments:
  production:
    baseUrl: "https://api.coze.com/v1"
    variables:
      apiKey: "${COZE_API_KEY}"
      authToken: "${COZE_AUTH_TOKEN}"
  
  staging:
    baseUrl: "https://api-staging.coze.com/v1"
    variables:
      apiKey: "${COZE_STAGING_KEY}"
      authToken: "${COZE_STAGING_TOKEN}"

tests:
  - name: "认证测试"
    requests:
      - name: "获取访问令牌"
        method: POST
        url: "{{baseUrl}}/auth/token"
        body:
          grant_type: "client_credentials"
          client_id: "test_client"
          client_secret: "test_secret"
        validate:
          - json: ".access_token"
            type: "string"
          - status: 200

  - name: "工作流生成测试"
    requests:
      - name: "生成电商工作流"
        method: POST
        url: "{{baseUrl}}/workflows/generate"
        headers:
          X-API-Key: "{{apiKey}}"
        body:
          name: "电商内容生成流程"
          description: "自动生成商品描述和营销内容的工作流"
          industry: "零售业"
          output_format: "coze_json"
          nodes:
            - type: "data_processing"
              config:
                prompt: "分析用户输入，生成商品描述"
        validate:
          - status: 201
          - json: ".result.download_url"
            type: "string"

  - name: "智能修复测试"
    requests:
      - name: "执行错误修复"
        method: POST
        url: "{{baseUrl}}/repair/execute"
        headers:
          X-API-Key: "{{apiKey}}"
        body:
          operationMode: "auto_repair"
          errorContext:
            errorCode: "101006"
            source: "plugin_metadata"
          repairLevel: "advanced"
        validate:
          - status: 200
          - json: ".fixedItems"
            type: "number"
            min: 0

  - name: "全场景处理测试"
    requests:
      - name: "统一入口测试"
        method: POST
        url: "{{baseUrl}}/universal-process"
        headers:
          X-API-Key: "{{apiKey}}"
        body:
          task_type: "error_repair"
          input:
            error_context:
              error_code: "101006"
              source: "workflow_canvas"
              affected_components: ["plugin_metadata"]
          options:
            repair_level: "deep"
            operation_mode: "auto"
            skip_backup: false
        validate:
          - status: 200
          - json: ".success"
            equals: true
"""
