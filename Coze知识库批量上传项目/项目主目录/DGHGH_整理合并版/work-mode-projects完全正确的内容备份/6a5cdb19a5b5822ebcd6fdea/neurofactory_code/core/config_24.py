openapi: 3.0.0
info:
  title: 企业工作流智能编排系统 API
  description: "统一的企业级工作流管理、自动化执行和智能编排平台，集成30个核心功能模块"
  version: "1.0.0"
  contact:
    name: "技术支持团队"
    email: "support@enterprise-workflow.com"
    url: "https://enterprise-workflow.com"
  license:
    name: "商业许可"
    url: "https://enterprise-workflow.com/license"

servers:
  - url: "https://api.enterprise-workflow.com/v1"
    description: "生产环境"
  - url: "https://staging-api.enterprise-workflow.com/v1"
    description: "测试环境"
  - url: "https://dev-api.enterprise-workflow.com/v1"
    description: "开发环境"

paths:
  /execute:
    post:
      operationId: "universalExecute"
      summary: "统一执行端点"
      description: "通过统一的API端点执行所有30种功能操作"
      tags:
        - "Universal Operations"
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UniversalRequest"
            examples:
              emergency_example:
                summary: "紧急模式激活示例"
                value:
                  operation_type: "activate_emergency"
                  operation_config:
                    emergency_config:
                      emergency_level: "critical"
                      activation_reason: "系统检测到严重安全威胁"
                      auto_recovery: true
                      recovery_strategy: "immediate"
                      notification_contacts: ["admin@company.com", "ops@company.com"]
                  version: "v2.0"
                  async_execution: false
                  validation_config:
                    auto_validate: true
                    validation_strictness: "strict"
              workflow_example:
                summary: "工作流生成示例"
                value:
                  operation_type: "generate_workflow"
                  operation_config:
                    workflow_config:
                      requirement_description: "需要创建一个电商订单处理工作流，包含库存检查、支付验证和物流分配"
                      business_domain: "ecommerce"
                      complexity_level: "medium"
                      validation_strictness: "standard"
                  version: "v1.0"
                  async_execution: true
                  callback_url: "https://webhook.company.com/callback"
              ai_enhancement_example:
                summary: "AI数据增强示例"
                value:
                  operation_type: "ai_enhancement"
                  operation_config:
                    ai_enhancement_config:
                      input_data: "需要清洗和增强的用户行为数据..."
                      enhancement_type: "cleaning"
                      output_format: "json"
                  version: "v1.0"
                  async_execution: false
      responses:
        "200":
          description: "操作执行成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UniversalResponse"
        "202":
          description: "异步操作已接受"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AsyncResponse"
        "400":
          description: "请求参数错误"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "401":
          description: "未授权访问"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "500":
          description: "服务器内部错误"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"

  /operations/{operation_id}:
    get:
      operationId: "getOperationStatus"
      summary: "获取操作状态"
      description: "查询异步操作的执行状态和结果"
      tags:
        - "Operation Monitoring"
      security:
        - bearerAuth: []
      parameters:
        - name: "operation_id"
          in: "path"
          required: true
          schema:
            type: "string"
          description: "操作ID"
      responses:
        "200":
          description: "操作状态信息"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OperationStatus"
        "404":
          description: "操作未找到"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"
        "500":
          description: "服务器内部错误"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"

  /validate:
    post:
      operationId: "validateOperationParameters"
      summary: "预验证操作参数"
      description: "在执行操作前验证参数的合法性"
      tags:
        - "Validation"
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UniversalRequest"
      responses:
        "200":
          description: "验证结果"
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  is_valid:
                    type: "boolean"
                  validation_errors:
                    type: "array"
                    items:
                      type: "object"
                      properties:
                        field:
                          type: "string"
                        error:
                          type: "string"
                        suggestion:
                          type: "string"
                  suggestions:
                    type: "array"
                    items:
                      type: "string"

  /health:
    get:
      operationId: "healthCheck"
      summary: "健康检查"
      description: "检查服务健康状态和各模块可用性"
      tags:
        - "System"
      responses:
        "200":
          description: "服务健康"
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  status:
                    type: "string"
                    enum: ["healthy", "degraded", "unhealthy"]
                  timestamp:
                    type: "string"
                    format: "date-time"
                  components:
                    type: "object"
                    properties:
                      workflow_engine:
                        type: "string"
                        enum: ["up", "down", "degraded"]
                      ai_services:
                        type: "string"
                        enum: ["up", "down", "degraded"]
                      system_ops:
                        type: "string"
                        enum: ["up", "down", "degraded"]
                      cultural_services:
                        type: "string"
                        enum: ["up", "down", "degraded"]
                      database:
                        type: "string"
                        enum: ["connected", "disconnected"]
                      cache:
                        type: "string"
                        enum: ["connected", "disconnected"]
                  version:
                    type: "string"
                  uptime:
                    type: "number"

components:
  schemas:
    UniversalRequest:
      type: "object"
      required:
        - "operation_type"
        - "operation_config"
      properties:
        operation_type:
          type: "string"
          enum:
            - "activate_emergency"
            - "ai_enhancement"
            - "analyze_industry"
            - "auto_repair"
            - "backup_revert"
            - "create_custom_node"
            - "create_workflow"
            - "delete_workflow"
            - "execute_workflow"
            - "feed_data"
            - "generate_workflow"
            - "get_data_connections"
            - "get_workflow_by_id"
            - "get_workflows"
            - "process_automation"
            - "process_luoyang_heritage"
            - "repair_all_nodes"
            - "train_model"
            - "trigger_auto_plugin_workflow"
            - "update_workflow"
            - "validate_parameters"
          description: "要执行的操作类型"
        operation_config:
          type: "object"
          description: "操作配置参数"
        version:
          type: "string"
          enum: ["v1.0", "v2.0", "v3.0"]
          default: "v1.0"
        async_execution:
          type: "boolean"
          default: false
        callback_url:
          type: "string"
          format: "uri"
        validation_config:
          type: "object"
          properties:
            auto_validate:
              type: "boolean"
            validation_strictness:
              type: "string"
              enum: ["relaxed", "standard", "strict"]
            error_handling:
              type: "string"
              enum: ["strict", "lenient", "adaptive"]

    UniversalResponse:
      type: "object"
      properties:
        success:
          type: "boolean"
        operation_id:
          type: "string"
        status:
          type: "string"
          enum: ["completed", "processing", "failed", "accepted"]
        result:
          type: "object"
        error:
          type: "object"
        execution_time:
          type: "number"
        timestamp:
          type: "string"
          format: "date-time"
        monitor_url:
          type: "string"
          format: "uri"

    AsyncResponse:
      type: "object"
      properties:
        success:
          type: "boolean"
        operation_id:
          type: "string"
        status:
          type: "string"
          enum: ["accepted"]
        monitor_url:
          type: "string"
          format: "uri"
        estimated_completion:
          type: "string"
          format: "date-time"

    OperationStatus:
      type: "object"
      properties:
        operation_id:
          type: "string"
        status:
          type: "string"
          enum: ["pending", "processing", "completed", "failed", "cancelled"]
        progress:
          type: "number"
          minimum: 0
          maximum: 100
        result:
          type: "object"
        error:
          type: "object"
        created_at:
          type: "string"
          format: "date-time"
        updated_at:
          type: "string"
          format: "date-time"
        estimated_remaining:
          type: "number"

    ErrorResponse:
      type: "object"
      required:
        - "error_code"
        - "message"
      properties:
        error_code:
          type: "string"
          enum:
            - "INVALID_PARAMS"
            - "UNAUTHORIZED"
            - "OPERATION_NOT_FOUND"
            - "SERVICE_UNAVAILABLE"
            - "RATE_LIMITED"
            - "INTERNAL_ERROR"
        message:
          type: "string"
        details:
          type: "object"
        timestamp:
          type: "string"
          format: "date-time"
        request_id:
          type: "string"

  securitySchemes:
    bearerAuth:
      type: "http"
      scheme: "bearer"
      bearerFormat: "JWT"

security:
  - bearerAuth: []