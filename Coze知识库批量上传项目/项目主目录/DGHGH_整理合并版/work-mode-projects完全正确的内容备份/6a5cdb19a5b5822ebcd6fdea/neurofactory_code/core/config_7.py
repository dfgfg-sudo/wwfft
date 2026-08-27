openapi: 3.1.0
info:
  title: Coze全场景智能自动化超级中枢 API
  description: |
    统一整合的智能自动化API中枢，支持多场景工作流自动化、数据集成与AI增强处理。
    整合AutoPluginMaster + QuantumAutomationMaster + OmniAutoMaster全栈能力。

    核心能力整合：
    1. 单一入口驱动：只需在工作流的最终输出节点输入自然语言需求
    2. 全自动逆向驱动：基于需求逆向推导前置插件节点、自动创建/配置/执行全链路
    3. 任意节点触发：任意节点输入需求均能驱动后续节点自动化
    4. 零手动配置：中间过程全透明，无需干预参数/连接/逻辑
    5. 全节点自愈：自动化检测修复工作流内所有节点（配置/逻辑/依赖）
    6. 端到端插件生成：输入功能描述即生成完整插件，自动注册到Coze
    7. 48项跨领域技术点整合：Coze平台开发/AI模型训练/自动化系统/媒体生成/健康管理/开发工具/跨领域应用

    🛠️ 整合工具列表：
    - AutoPluginMaster: 端到端自动化插件生成系统
    - QuantumAutomationMaster: 量子级自动化处理引擎
    - OmniAutoMaster: 全栈智能自动化中枢
    - 工作流自动化系统
    - 节点自愈引擎
    - AI增强处理器
    - 数据集成连接器

    ⚙️ 用户控制选项：
    - 启用/禁用全自动处理模式
    - 选择操作类型：工作流管理/插件生成/节点修复/AI增强/数据集成/全自动
    - 设置自动化修复级别：基础/高级/完整
    - 配置进度通知偏好：静默/关键步骤/详细

    🚀 核心诉求总结：
    只需在结束点输入需求，全程自动完成的核心目标，并支持"在任意点输入需求，驱动后续自动化"的增强模式。
  version: 10.1.0
  contact:
    name: API支持团队
    email: support@coze-automation.com
    url: https://api.coze-automation.com/docs
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html

servers:
  - url: https://api.coze.com
    description: Coze官方API服务器
  - url: https://plugin.coze.cn/v1
    description: Coze插件官方服务器
  - url: https://api.coze-automation.com/v1
    description: 生产环境API服务器

tags:
  - name: 工作流自动化
    description: 全自动工作流生成与执行
  - name: 插件生成
    description: 端到端插件自动生成系统
  - name: 节点自愈
    description: 工作流节点自动检测修复
  - name: 智能触发
    description: 任意节点输入触发自动化
  - name: AI增强
    description: AI能力集成与增强处理
  - name: 数据集成
    description: 多源数据连接与同步
  - name: 统一自动化工具
    description: 全功能智能自动化处理中枢

paths:
  # 统一全能入口
  /open_api/v1/chat:
    post:
      operationId: universalAutomationProcessor
      summary: 全能自动化处理
      description: |
        🎯 用户只需输入自然语言需求，系统自动识别意图并完成工作流管理、插件生成、节点修复、AI增强、数据集成等所有操作

        📋 支持的操作类型：
        - workflow_management: 工作流管理（创建/更新/执行）
        - plugin_generation: 插件生成（端到端自动生成）
        - node_repair: 节点自愈（全节点批量修复）
        - ai_enhancement: AI增强（数据摘要/翻译/分类/提取）
        - data_integration: 数据集成（多源连接同步）
        - full_automation: 全自动处理（从需求到完成的完整流程）
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - user_input
              properties:
                user_input:
                  type: string
                  minLength: 1
                  description: 请输入您的需求描述
                  example: "创建一个每天自动备份数据库到云存储的工作流"
                auto_mode:
                  type: boolean
                  description: 是否启用全自动模式
                  default: true
                automation_level:
                  type: string
                  enum: [full, assisted, manual]
                  default: full
                output_format:
                  type: string
                  enum: [complete_plugin, workflow_definition, api_specification]
                  default: complete_plugin
            examples:
              全自动模式示例:
                summary: 全自动处理模式
                value:
                  user_input: "创建实时股票监控系统：监控AAPL、GOOGL股票，价格波动超过5%时发送警报到邮箱，并生成每日报告"
                  enable_automation: true
                  automation_level: "full"
                  output_format: "complete_plugin"
              半自动模式示例:
                summary: 半自动处理模式
                value:
                  user_input: "需要数据同步工作流，从数据库A同步到数据仓库B"
                  enable_automation: false
                  automation_level: "assisted"
                  output_format: "workflow_definition"
      responses:
        '200':
          description: 自动化处理成功完成
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  execution_id:
                    type: string
                  detected_intent:
                    type: string
                    enum: [workflow_management, plugin_generation, node_repair, ai_enhancement, data_integration, full_automation]
                  automated_tasks:
                    type: array
                    items:
                      type: object
                  generated_outputs:
                    type: object
                    properties:
                      workflows:
                        type: array
                        items:
                          type: object
                      plugins:
                        type: array
                        items:
                          type: object
                      repairs:
                        type: array
                        items:
                          type: object
                      ai_results:
                        type: array
                        items:
                          type: object
                      data_connections:
                        type: array
                        items:
                          type: object
                  execution_metrics:
                    type: object
                  intelligent_suggestions:
                    type: array
                    items:
                      type: object
                  user_friendly_summary:
                    type: string
      security:
        - CozeApiKey: []

  # 工作流管理端点
  /workflows:
    get:
      tags: [工作流自动化]
      summary: 获取工作流列表
      operationId: getWorkflows
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
        - $ref: '#/components/parameters/FilterParam'
        - $ref: '#/components/parameters/SortParam'
      responses:
        '200':
          description: 成功获取工作流列表
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowListResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

    post:
      tags: [工作流自动化]
      summary: 创建工作流
      operationId: createWorkflow
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkflowCreateRequest'
      responses:
        '201':
          description: 成功创建工作流
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

  /workflows/{workflowId}:
    get:
      tags: [工作流自动化]
      summary: 获取工作流详情
      operationId: getWorkflowById
      parameters:
        - $ref: '#/components/parameters/WorkflowIdParam'
      responses:
        '200':
          description: 成功获取工作流详情
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowDetailResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '404':
          $ref: '#/components/responses/404Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

    put:
      tags: [工作流自动化]
      summary: 更新工作流
      operationId: updateWorkflow
      parameters:
        - $ref: '#/components/parameters/WorkflowIdParam'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkflowUpdateRequest'
      responses:
        '200':
          description: 成功更新工作流
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '404':
          $ref: '#/components/responses/404Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

    delete:
      tags: [工作流自动化]
      summary: 删除工作流
      operationId: deleteWorkflow
      parameters:
        - $ref: '#/components/parameters/WorkflowIdParam'
      responses:
        '204':
          description: 成功删除工作流
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '404':
          $ref: '#/components/responses/404Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

  /workflows/{workflowId}/execute:
    post:
      tags: [工作流自动化]
      summary: 执行工作流
      operationId: executeWorkflow
      parameters:
        - $ref: '#/components/parameters/WorkflowIdParam'
      requestBody:
        required: false
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkflowExecuteRequest'
      responses:
        '202':
          description: 已接受执行请求
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowExecutionResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '404':
          $ref: '#/components/responses/404Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

  /workflows/trigger:
    post:
      tags: [工作流自动化, 插件生成, 智能触发]
      summary: 触发全自动插件生成+工作流执行
      description: 输入描述生成插件，并自动创建工作流执行链，支持任意节点触发和全节点自愈
      operationId: triggerAutoPluginWorkflow
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AutoPluginTriggerRequest'
            examples:
              插件生成示例:
                value:
                  user_demand: "创建实时股票监控插件：输入股票代码+波动阈值，价格超阈值时发送邮件警报"
                  trigger_node_id: "end"
                  auto_repair_level: "full"
                  error_masking_level: "full"
              任意节点触发示例:
                value:
                  user_demand: "基于上述股票插件，生成近7天波动报告"
                  trigger_node_id: "quantum_plugin_generator"
                  auto_repair_level: "advanced"
      responses:
        '200':
          description: 插件生成+工作流执行成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AutoPluginSuccessResponse'
        '400':
          description: 参数错误
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - CozeApiKey: []

  /workflows/repair/all-nodes:
    post:
      tags: [节点自愈, 工作流自动化]
      summary: 工作流全节点批量自愈
      description: 自动化检测并修复工作流内所有节点（配置/逻辑/依赖），无需人工干预
      operationId: repairAllNodes
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AllNodeRepairRequest'
      responses:
        '200':
          description: 全节点修复成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AllNodeRepairResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '404':
          $ref: '#/components/responses/404Error'
      security:
        - CozeApiKey: []

  /automation/process:
    post:
      tags: [统一自动化工具]
      summary: 统一智能自动化处理
      description: 集成所有自动化功能的统一入口
      operationId: unifiedAutomationProcess
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UnifiedAutomationRequest'
      responses:
        '200':
          description: 处理成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedAutomationResponse'
        '400':
          $ref: '#/components/responses/400Error'

  /automation/repair:
    post:
      tags: [统一自动化工具]
      summary: 智能节点自愈
      operationId: smartNodeRepair
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RepairRequest'
      responses:
        '200':
          description: 修复成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RepairResponse'

  /automation/ai-enhancement:
    post:
      tags: [统一自动化工具]
      summary: AI增强处理
      operationId: aiEnhancement
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AIEnhancementRequest'
      responses:
        '200':
          description: 增强成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AIEnhancementResponse'

  /data/connections:
    get:
      tags: [数据集成]
      summary: 获取数据连接列表
      operationId: getDataConnections
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/LimitParam'
        - $ref: '#/components/parameters/ConnectionTypeParam'
      responses:
        '200':
          description: 成功获取数据连接列表
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DataConnectionListResponse'
        '400':
          $ref: '#/components/responses/400Error'
        '401':
          $ref: '#/components/responses/401Error'
        '500':
          $ref: '#/components/responses/500Error'
      security:
        - BearerAuth: []

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
    CozeApiKey:
      type: apiKey
      in: header
      name: X-Coze-API-Key

  parameters:
    PageParam:
      name: page
      in: query
      description: 页码，从1开始
      required: false
      schema:
        type: integer
        minimum: 1
        default: 1
    LimitParam:
      name: limit
      in: query
      description: 每页记录数
      required: false
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
    FilterParam:
      name: filter
      in: query
      description: 过滤条件(JSON格式)
      required: false
      schema:
        type: string
    SortParam:
      name: sort
      in: query
      description: 排序字段和方向(格式: field1:asc,field2:desc)
      required: false
      schema:
        type: string
    WorkflowIdParam:
      name: workflowId
      in: path
      description: 工作流唯一标识符
      required: true
      schema:
        type: string
    ConnectionTypeParam:
      name: type
      in: query
      description: 连接类型过滤
      required: false
      schema:
        type: string
        enum: [database, api, file, messaging]

  schemas:
    AutoPluginTriggerRequest:
      type: object
      required: [user_demand]
      properties:
        user_demand:
          type: string
          minLength: 1
        trigger_node_id:
          type: string
          default: "end"
        auto_repair_level:
          type: string
          enum: [basic, advanced, full]
          default: "full"
        error_masking_level:
          type: string
          enum: [none, partial, full]
          default: "full"
        workflow_id:
          type: string
        plugin_registry:
          type: boolean
          default: true

    AllNodeRepairRequest:
      type: object
      required: [workflow_id]
      properties:
        workflow_id:
          type: string
        repair_scope:
          type: string
          enum: [config, logic, dependency, all]
          default: "all"

    AutoPluginSuccessResponse:
      type: object
      properties:
        code:
          type: integer
          enum: [0]
        message:
          type: string
          enum: ["success"]
        data:
          type: object
          properties:
            workflow_id:
              type: string
            execution_id:
              type: string
            generated_plugin:
              type: object
              properties:
                plugin_name:
                  type: string
                coze_import_command:
                  type: string
            node_repair_summary:
              type: object

    AllNodeRepairResponse:
      type: object
      properties:
        code:
          type: integer
          enum: [0]
        message:
          type: string
          enum: ["all_nodes_repaired"]
        data:
          type: object
          properties:
            workflow_id:
              type: string
            repair_details:
              type: array
              items:
                type: object
            workflow_available:
              type: boolean

    WorkflowCreateRequest:
      type: object
      required: [name, version, definition]
      properties:
        name:
          type: string
          maxLength: 100
        description:
          type: string
          maxLength: 500
        version:
          type: string
        definition:
          type: object
        enabled:
          type: boolean
          default: true

    WorkflowUpdateRequest:
      type: object
      properties:
        name:
          type: string
          maxLength: 100
        description:
          type: string
          maxLength: 500
        version:
          type: string
        definition:
          type: object
        enabled:
          type: boolean

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
        version:
          type: string
        status:
          type: string
          enum: [active, inactive, draft]
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    WorkflowDetailResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        description:
          type: string
        version:
          type: string
        definition:
          type: object
        status:
          type: string
        executionHistory:
          type: array
          items:
            type: object

    WorkflowListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/WorkflowResponse'
        pagination:
          $ref: '#/components/schemas/PaginationInfo'

    WorkflowExecuteRequest:
      type: object
      properties:
        parameters:
          type: object
        async:
          type: boolean
          default: false

    WorkflowExecutionResponse:
      type: object
      properties:
        executionId:
          type: string
          format: uuid
        status:
          type: string
          enum: [accepted, running, completed, failed]
        startedAt:
          type: string
          format: date-time
        results:
          type: object

    UnifiedAutomationRequest:
      type: object
      required: [user_input]
      properties:
        user_input:
          type: string
        enable_automation:
          type: boolean
          default: true
        automation_level:
          type: string
          enum: [full, assisted, manual]
          default: full
        output_format:
          type: string
          enum: [complete_plugin, workflow_definition, api_specification]
          default: complete_plugin

    UnifiedAutomationResponse:
      type: object
      properties:
        success:
          type: boolean
        data:
          type: object
        metadata:
          type: object

    RepairRequest:
      type: object
      required: [workflow_id]
      properties:
        workflow_id:
          type: string
        repair_scope:
          type: string
          enum: [config, logic, dependency, all]
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
          $ref: '#/components/schemas/RepairSummary'
        repaired_nodes:
          type: array
          items:
            $ref: '#/components/schemas/RepairedNode'

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
          enum: [success, failed]

    DataConnection:
      type: object
      required: [name, type, config]
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
        type:
          type: string
          enum: [database, api, file, messaging]
        config:
          type: object

    DataConnectionListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/DataConnection'
        pagination:
          $ref: '#/components/schemas/PaginationInfo'

    AIEnhancementRequest:
      type: object
      required: [input, enhancement_type]
      properties:
        input:
          type: object
        enhancement_type:
          type: string
          enum: [summarize, translate, classify, extract, generate]
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
      description: 请求参数错误
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    401Error:
      description: 未授权访问
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    404Error:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
    500Error:
      description: 服务器内部错误
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

externalDocs:
  description: Coze API 完整文档
  url: https://docs.coze-automation.com