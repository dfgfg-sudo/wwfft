openapi: 3.1.0
info:
  title: "终极统一智能自动化超级中枢"
  version: "15.0.0-Enterprise-Complete"
  description: "全插件深度融合版｜58项核心功能统一调度｜智能路由决策｜跨工作流协同｜全链路监控｜企业级统一整合的智能自动化API中枢，支持多场景工作流自动化、数据集成与AI增强处理"
  contact:
    name: "智能自动化实验室 & 企业API支持团队"
    url: "https://docs.unified-automation.com"
    email: "enterprise-support@unified-automation.com"
  license:
    name: "Apache 2.0"
    url: "https://www.apache.org/licenses/LICENSE-2.0.html"
externalDocs:
  description: "完整API文档和企业使用指南"
  url: "https://docs.unified-automation.com/enterprise"
servers:
  - url: "https://api.unified-automation.com/v15"
    description: "统一生产环境API服务器"
  - url: "https://api.coze.com/v3"
    description: "Coze官方API服务端"
tags:
  - name: "统一执行"
    description: "统一超级中枢执行入口"
  - name: "智能路由"
    description: "智能路由决策引擎"
  - name: "工作流编排"
    description: "跨工作流编排系统"
  - name: "插件生态"
    description: "统一插件生态系统"
  - name: "数据智能"
    description: "数据智能处理引擎"
  - name: "领域专业"
    description: "领域专业化处理"
  - name: "系统管理"
    description: "系统管理和监控"
paths:
  /execute:
    post:
      operationId: "unifiedExecute"
      summary: "统一执行入口"
      description: "通过统一入口执行所有功能，支持智能路由和参数映射"
      tags: ["统一执行"]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UnifiedExecutionRequest"
      responses:
        "200":
          description: "执行成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UnifiedExecutionResponse"
        "202":
          description: "异步执行已接受"
          content:
            application/json:
              schema:
                type: object
                properties:
                  execution_id:
                    type: string
                  status:
                    type: string
                    enum: ["accepted"]
                  monitor_url:
                    type: string
                    format: uri
        "400":
          description: "请求参数错误"
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

  /unified-automation/execute:
    post:
      tags: ["统一执行"]
      summary: "执行统一自动化任务"
      operationId: "executeUnifiedAutomation"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: ["user_input"]
              properties:
                action_type:
                  type: string
                  enum: ["plugin_generation", "workflow_automation", "node_repair", "smart_trigger", "full_pipeline"]
                user_input:
                  type: string
                enable_automation:
                  type: boolean
                  default: true
                automation_level:
                  type: string
                  enum: ["basic", "advanced", "full"]
                  default: "full"
                auto_repair_params:
                  type: boolean
                  default: true
                features:
                  type: object
                  properties:
                    plugin_generation: {type: boolean, default: true}
                    workflow_creation: {type: boolean, default: true}
                    node_auto_repair: {type: boolean, default: true}
                    smart_trigger: {type: boolean, default: true}
                    param_validation: {type: boolean, default: true}
      responses:
        "200":
          description: "执行成功"
          content:
            application/json:
              schema:
                type: object
                properties:
                  success: {type: boolean}
                  task_id: {type: string}
                  execution_summary:
                    type: object
                    properties:
                      plugins_generated: {type: integer}
                      workflows_created: {type: integer}
                      nodes_repaired: {type: integer}
                      params_fixed: {type: integer}
                      execution_time_ms: {type: integer}
                  results:
                    type: object
                    properties:
                      generated_plugins:
                        type: array
                        items:
                          type: object
                          properties:
                            name: {type: string}
                            import_command: {type: string}
                            status: {type: string}
                      workflow_status:
                        type: object
                        properties:
                          id: {type: string}
                          status: {type: string}
                          execution_count: {type: integer}
                      repair_report:
                        type: object
                        properties:
                          scanned_nodes: {type: integer}
                          fixed_errors: {type: integer}
                          success_rate: {type: string}
        "400":
          description: "请求参数错误"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"

  /workflows/trigger:
    post:
      tags: ["工作流自动化", "插件生态"]
      summary: "触发全自动插件生成+工作流执行"
      operationId: "triggerAutoPluginWorkflow"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/AutoPluginTriggerRequest"
      responses:
        "200":
          description: "成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AutoPluginSuccessResponse"
      security:
        - CozeApiKey: []

  /workflows/repair/all-nodes:
    post:
      tags: ["节点自愈"]
      summary: "工作流全节点批量自愈"
      operationId: "repairAllNodes"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_id: {type: string}
                repair_scope:
                  type: string
                  enum: ["config", "logic", "dependency", "all"]
                  default: "all"
              required: ["workflow_id"]
      responses:
        "200":
          description: "修复成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AllNodeRepairResponse"

  /system/health:
    get:
      tags: ["系统管理"]
      summary: "健康检查"
      operationId: "healthCheck"
      responses:
        "200":
          description: "系统健康"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/HealthCheckResponse"

components:
  securitySchemes:
    UnifiedApiKey:
      type: apiKey
      in: header
      name: X-API-Key
    CozeApiKey:
      type: apiKey
      in: header
      name: Authorization
      description: "格式：Bearer {{secrets.COZE_API_KEY}}"
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    UnifiedExecutionRequest:
      type: object
      required: ["operation_intent"]
      properties:
        operation_intent:
          type: string
          description: "操作意图描述"
        execution_mode:
          type: string
          enum: ["auto", "manual", "hybrid"]
          default: "auto"
        priority:
          type: string
          enum: ["low", "normal", "high", "critical"]
          default: "normal"
        smart_parameters:
          type: object
          properties:
            auto_detect_plugins:
              type: boolean
              default: true
            parameter_mapping_strategy:
              type: string
              enum: ["strict", "flexible", "ai_optimized"]
              default: "ai_optimized"
            enable_automation:
              type: boolean
              default: true

    UnifiedExecutionResponse:
      type: object
      properties:
        success: {type: boolean}
        execution_id: {type: string}
        results: {type: object}
        execution_time: {type: number}
        timestamp: {type: string, format: date-time}

    AutoPluginTriggerRequest:
      type: object
      required: ["user_demand"]
      properties:
        user_demand: {type: string, minLength: 1}
        trigger_node_id: {type: string, default: "end"}
        auto_repair_level: {type: string, enum: ["basic", "advanced", "full"], default: "full"}
        error_masking_level: {type: string, enum: ["none", "partial", "full"], default: "full"}
        plugin_registry: {type: boolean, default: true}

    AutoPluginSuccessResponse:
      type: object
      properties:
        code: {type: integer, enum: [0]}
        message: {type: string, enum: ["success"]}
        data:
          type: object
          properties:
            workflow_id: {type: string}
            execution_id: {type: string}
            generated_plugin:
              type: object
              properties:
                plugin_name: {type: string}
                coze_import_command: {type: string}
            node_repair_summary:
              type: object
              properties:
                total_nodes: {type: integer}
                repaired_nodes: {type: integer}
                repair_success_rate: {type: string}

    AllNodeRepairResponse:
      type: object
      properties:
        code: {type: integer, enum: [0]}
        message: {type: string, enum: ["all_nodes_repaired"]}
        data:
          type: object
          properties:
            workflow_id: {type: string}
            repair_details:
              type: array
              items:
                type: object
                properties:
                  node_id: {type: string}
                  error_type: {type: string}
                  repair_status: {type: string, enum: ["success", "failed"]}
            workflow_available: {type: boolean}

    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            code: {type: string}
            message: {type: string}
            details: {type: array}
            timestamp: {type: string, format: date-time}

    HealthCheckResponse:
      type: object
      properties:
        components: {type: object}
        status: {type: string, enum: ["healthy", "degraded", "unhealthy"]}
        timestamp: {type: string, format: date-time}
        uptime: {type: number}
        version: {type: string}

security:
  - BearerAuth: []
  - UnifiedApiKey: []