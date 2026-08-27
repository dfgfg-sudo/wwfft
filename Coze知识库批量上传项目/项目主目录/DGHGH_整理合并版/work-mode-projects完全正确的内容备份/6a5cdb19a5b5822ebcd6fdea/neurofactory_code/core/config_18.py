openapi: 3.0.3
info:
  title: "Coze全场景智能自动化超级中枢"
  description: |
    # 统一智能自动化工具
    
    ## 核心功能整合
    
    ### 1. 工作流自动化系统
    - 智能工作流创建与管理
    - 多触发器支持（定时、事件、手动）
    - 实时执行监控和性能分析
    
    ### 2. AI插件生成引擎  
    - 自然语言需求解析
    - 自动代码生成和测试
    - 一键部署到Coze平台
    
    ### 3. 全节点自愈系统
    - 实时健康监测和故障诊断
    - 智能配置修复和依赖管理
    - 自动化性能优化
    
    ### 4. 数据集成中心
    - 多源数据连接和同步
    - AI增强数据处理
    - 统一数据质量管理
    
    ## 使用方式
    用户可以通过设置`enable_automation`参数选择是否启用全自动处理模式
    
    ## 技术特性
    - 端到端自动化：输入描述即得完整解决方案
    - 零手动配置：中间过程全透明，无需干预参数
    - 智能自愈：自动检测修复所有节点问题
    - 企业级可靠：高可用架构，数据安全保障
  version: "10.1.0"
  contact:
    name: "API支持团队"
    email: "support@coze-automation.com"
    url: "https://api.coze-automation.com/docs"
  license:
    name: "Apache 2.0"
    url: "https://www.apache.org/licenses/LICENSE-2.0.html"

servers:
  - url: "https://api.coze-automation.com/v1"
    description: "生产环境API服务器"

tags:
  - name: "智能自动化"
    description: "全功能智能自动化处理，支持工作流、插件生成、节点自愈等所有功能"

paths:
  /automation/process:
    post:
      tags:
        - "智能自动化"
      summary: "统一智能自动化处理"
      description: "集成所有自动化功能的统一入口，支持用户选择是否启用全自动处理模式"
      operationId: "unifiedAutomationProcess"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/UnifiedAutomationRequest"
            examples:
              全自动模式示例:
                summary: "全自动处理模式"
                value:
                  user_input: "创建实时股票监控系统：监控AAPL、GOOGL股票，价格波动超过5%时发送警报到邮箱，并生成每日报告"
                  enable_automation: true
                  automation_level: "full"
                  output_format: "complete_plugin"
              半自动模式示例:
                summary: "半自动处理模式"
                value:
                  user_input: "需要数据同步工作流，从数据库A同步到数据仓库B"
                  enable_automation: false
                  automation_level: "assisted"
                  output_format: "workflow_definition"
      responses:
        '200':
          description: "自动化处理成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UnifiedAutomationResponse"
        '400':
          description: "请求参数错误"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ErrorResponse"

  /automation/workflows:
    get:
      tags:
        - "智能自动化"
      summary: "获取工作流列表"
      description: "获取所有工作流列表，支持分页和过滤"
      operationId: "getAllWorkflows"
      parameters:
        - $ref: "#/components/parameters/PageParam"
        - $ref: "#/components/parameters/LimitParam"
        - $ref: "#/components/parameters/FilterParam"
      responses:
        '200':
          description: "成功获取工作流列表"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/WorkflowListResponse"

  /automation/workflows/{workflowId}:
    put:
      tags:
        - "智能自动化"
      summary: "更新工作流"
      description: "更新现有工作流定义"
      operationId: "updateWorkflow"
      parameters:
        - $ref: "#/components/parameters/WorkflowIdParam"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/WorkflowUpdateRequest"
      responses:
        '200':
          description: "成功更新工作流"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/WorkflowResponse"

  /automation/repair:
    post:
      tags:
        - "智能自动化"
      summary: "智能节点自愈"
      description: "自动化检测并修复工作流内所有节点问题"
      operationId: "smartNodeRepair"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/RepairRequest"
      responses:
        '200':
          description: "节点修复成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/RepairResponse"

  /automation/ai-enhancement:
    post:
      tags:
        - "智能自动化"
      summary: "AI增强处理"
      description: "使用AI能力对输入数据进行增强处理"
      operationId: "aiEnhancement"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/AIEnhancementRequest"
      responses:
        '200':
          description: "AI增强处理成功"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AIEnhancementResponse"

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  parameters:
    PageParam:
      name: page
      in: query
      description: "页码，从1开始"
      required: false
      schema:
        type: integer
        minimum: 1
        default: 1
    LimitParam:
      name: limit
      in: query
      description: "每页记录数"
      required: false
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
    FilterParam:
      name: filter
      in: query
      description: "过滤条件(JSON格式)"
      required: false
      schema:
        type: string
    WorkflowIdParam:
      name: workflowId
      in: path
      description: "工作流唯一标识符"
      required: true
      schema:
        type: string
        pattern: "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"

  schemas:
    UnifiedAutomationRequest:
      type: object
      required:
        - user_input
      properties:
        user_input:
          type: string
          description: "用户输入的自然语言需求"
          examples:
            - "创建实时股票监控系统"
            - "构建数据同步工作流从MySQL到数据仓库"
            - "开发用户行为分析插件"
        enable_automation:
          type: boolean
          default: true
          description: "是否启用全自动处理模式"
        automation_level:
          type: string
          enum:
            - full
            - assisted
            - manual
          default: full
          description: "自动化级别"
        output_format:
          type: string
          enum:
            - complete_plugin
            - workflow_definition
            - api_specification
          default: complete_plugin
          description: "输出格式"
        options:
          type: object
          description: "附加选项"

    UnifiedAutomationResponse:
      type: object
      properties:
        success:
          type: boolean
          description: "处理是否成功"
        data:
          type: object
          properties:
            generated_content:
              type: object
              description: "生成的内容"
            workflow_definition:
              $ref: "#/components/schemas/WorkflowDefinition"
            plugin_specification:
              type: object
              description: "插件规范"
            execution_results:
              type: object
              description: "执行结果"
            repair_summary:
              $ref: "#/components/schemas/RepairSummary"
        metadata:
          type: object
          properties:
            processing_time:
              type: number
              description: "处理时间(秒)"
            automation_level_used:
              type: string
              description: "实际使用的自动化级别"
            generated_components:
              type: array
              items:
                type: string
              description: "生成的组件列表"

    WorkflowDefinition:
      type: object
      properties:
        version:
          type: string
          default: "1.0"
        triggers:
          type: array
          items:
            $ref: "#/components/schemas/WorkflowTrigger"
        steps:
          type: array
          items:
            $ref: "#/components/schemas/WorkflowStep"
        outputs:
          type: array
          items:
            $ref: "#/components/schemas/WorkflowOutput"

    WorkflowTrigger:
      type: object
      properties:
        type:
          type: string
          enum:
            - schedule
            - webhook
            - event
            - manual
        config:
          type: object

    WorkflowStep:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        type:
          type: string
          enum:
            - action
            - condition
            - loop
            - delay
        action:
          type: string
        parameters:
          type: object
        onSuccess:
          type: string
        onFailure:
          type: string

    WorkflowOutput:
      type: object
      properties:
        name:
          type: string
        valueFrom:
          type: string

    WorkflowListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/WorkflowResponse"
        pagination:
          $ref: "#/components/schemas/PaginationInfo"

    WorkflowResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        status:
          type: string
          enum:
            - active
            - inactive
            - draft
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    WorkflowUpdateRequest:
      type: object
      properties:
        name:
          type: string
        description:
          type: string
        definition:
          $ref: "#/components/schemas/WorkflowDefinition"
        enabled:
          type: boolean

    RepairRequest:
      type: object
      required:
        - workflow_id
      properties:
        workflow_id:
          type: string
        repair_scope:
          type: string
          enum:
            - config
            - logic
            - dependency
            - all
          default: all
        auto_fix:
          type: boolean
          default: true

    RepairResponse:
      type: object
      properties:
        success:
          type: boolean
        repair_summary:
          $ref: "#/components/schemas/RepairSummary"
        repaired_nodes:
          type: array
          items:
            $ref: "#/components/schemas/RepairedNode"

    RepairSummary:
      type: object
      properties:
        total_nodes:
          type: integer
        repaired_count:
          type: integer
        failed_count:
          type: integer
        success_rate:
          type: string
        repair_duration_ms:
          type: integer

    RepairedNode:
      type: object
      properties:
        node_id:
          type: string
        node_type:
          type: string
        error_type:
          type: string
        repair_action:
          type: string
        repair_status:
          type: string
          enum:
            - success
            - failed

    AIEnhancementRequest:
      type: object
      required:
        - input
        - enhancement_type
      properties:
        input:
          type: object
        enhancement_type:
          type: string
          enum:
            - summarize
            - translate
            - classify
            - extract
            - generate
        options:
          type: object

    AIEnhancementResponse:
      type: object
      properties:
        enhanced_data:
          type: object
        metadata:
          type: object
        processing_time:
          type: number

    PaginationInfo:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        limit:
          type: integer
        pages:
          type: integer

    ErrorResponse:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: array
              items:
                type: object
            timestamp:
              type: string
              format: date-time

  responses:
    400Error:
      description: "请求参数错误"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"
          example:
            error:
              code: "VALIDATION_ERROR"
              message: "请求参数验证失败"
              details:
                - field: "user_input"
                  message: "用户输入不能为空"
              timestamp: "2023-05-15T10:00:00Z"
    500Error:
      description: "服务器内部错误"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/ErrorResponse"