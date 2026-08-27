openapi: 3.0.3
info:
  title: CompleteAIWorkflowAutomationPlatform API
  description: |
    Complete AI workflow automation platform with integrated emergency activation, data enhancement, industry analysis, self-healing backup recovery, custom node development, workflow lifecycle management, intelligent generation, data connectivity, process orchestration, cultural heritage processing, model training, plugin automation and parameter validation.
    
    完整AI工作流自动化平台，集成了紧急激活、数据增强、行业分析、自愈备份恢复、自定义节点开发、工作流生命周期管理、智能生成、数据连接、流程编排、文化遗产处理、模型训练、插件自动化和参数验证。
  version: 1.0.0
  contact:
    name: AI Workflow Platform Team
    email: support@aiworkflowplatform.com
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0

servers:
  - url: https://api.aiworkflowplatform.com/v1
    description: Production API server
  - url: https://staging-api.aiworkflowplatform.com/v1
    description: Staging API server
  - url: https://dev-api.aiworkflowplatform.com/v1
    description: Development API server

paths:
  /operations/execute:
    post:
      operationId: executeUnifiedOperation
      summary: Execute unified platform operation
      description: |
        Execute operations across all platform capabilities including emergency activation, AI enhancement, industry analysis, auto-repair, backup recovery, custom node creation, workflow management, data feeding, automated generation, data connection management, process automation, cultural heritage processing, model training, plugin automation and parameter validation.
      tags:
        - UnifiedOperations
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UnifiedOperationRequest'
            examples:
              emergency_activation:
                summary: Emergency activation example
                value:
                  operation_mode: "emergency_activation"
                  input_data:
                    emergency_type: "system_failure"
                    severity: "critical"
                    recovery_priority: "high"
                    affected_components: ["database", "api_gateway"]
                    automatic_recovery: true
              ai_enhancement:
                summary: AI enhancement example
                value:
                  operation_mode: "ai_enhancement"
                  input_data:
                    data_type: "text"
                    enhancement_type: "semantic_enrichment"
                    input_text: "Sample text for enhancement"
                    quality_threshold: 0.9
              industry_analysis:
                summary: Industry analysis example
                value:
                  operation_mode: "industry_analysis"
                  input_data:
                    industry: "technology"
                    analysis_type: "market_trends"
                    time_period: "2024"
                    geographic_scope: "global"
                    analysis_depth: "comprehensive"
                  industry_type: "technology"
      responses:
        '200':
          description: Operation executed successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedOperationResponse'
        '400':
          description: Invalid request parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /health:
    get:
      operationId: healthCheck
      summary: Health check endpoint
      tags:
        - SystemManagement
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  timestamp:
                    type: string
                    format: date-time
                  version:
                    type: string
                    example: "1.0.0"

  /supported-operations:
    get:
      operationId: getSupportedOperations
      summary: Get supported operations list
      tags:
        - SystemManagement
      responses:
        '200':
          description: List of supported operations
          content:
            application/json:
              schema:
                type: object
                properties:
                  supported_operations:
                    type: array
                    items:
                      type: object
                      properties:
                        operation_mode:
                          type: string
                        description:
                          type: string
                        required_parameters:
                          type: array
                          items:
                            type: string
                  timestamp:
                    type: string
                    format: date-time

  /workflows/{workflow_id}:
    get:
      operationId: getWorkflowDetails
      summary: Get specific workflow details by ID
      tags:
        - WorkflowManagement
      parameters:
        - name: workflow_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Workflow details retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  workflow_id:
                    type: string
                  name:
                    type: string
                  status:
                    type: string
                  nodes:
                    type: array
                    items:
                      type: object
                  connections:
                    type: array
                    items:
                      type: object
                  created_at:
                    type: string
                    format: date-time
                  updated_at:
                    type: string
                    format: date-time
        '404':
          description: Workflow not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /workflows:
    get:
      operationId: listWorkflows
      summary: List all accessible workflows
      tags:
        - WorkflowManagement
      parameters:
        - name: page
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: status
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Workflows list retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  workflows:
                    type: array
                    items:
                      type: object
                      properties:
                        workflow_id:
                          type: string
                        name:
                          type: string
                        status:
                          type: string
                        created_at:
                          type: string
                          format: date-time
                  pagination:
                    type: object
                    properties:
                      total:
                        type: integer
                      page:
                        type: integer
                      limit:
                        type: integer
                      total_pages:
                        type: integer

  /data-connections:
    get:
      operationId: listDataConnections
      summary: List all configured data connections
      tags:
        - DataManagement
      responses:
        '200':
          description: Data connections list retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  connections:
                    type: array
                    items:
                      type: object
                      properties:
                        connection_id:
                          type: string
                        name:
                          type: string
                        type:
                          type: string
                        status:
                          type: string
                        created_at:
                          type: string
                          format: date-time

components:
  schemas:
    UnifiedOperationRequest:
      type: object
      required:
        - operation_mode
        - input_data
      properties:
        operation_mode:
          type: string
          enum:
            - emergency_activation
            - ai_enhancement
            - industry_analysis
            - auto_repair
            - backup_recovery
            - custom_node_creation
            - workflow_management
            - data_feeding
            - automated_generation
            - data_connection_management
            - process_automation
            - cultural_heritage_processing
            - model_training
            - plugin_automation
            - parameter_validation
        input_data:
          type: object
        workflow_id:
          type: string
        backup_id:
          type: string
        node_config:
          type: object
        training_data:
          type: array
          items:
            type: object
        plugin_description:
          type: string
        validation_rules:
          type: object
        industry_type:
          type: string
        heritage_category:
          type: string
        repair_level:
          type: string
          enum: [low, medium, high, critical]
        generation_template:
          type: string
        emergency_type:
          type: string
          enum: [system_failure, security_breach, performance_degradation, data_corruption]
        severity:
          type: string
          enum: [low, medium, high, critical]
        data_type:
          type: string
          enum: [text, image, audio, video, tabular, time_series]
        enhancement_type:
          type: string
          enum: [semantic_enrichment, quality_improvement, feature_extraction, pattern_recognition, anomaly_detection]
        analysis_type:
          type: string
          enum: [market_trends, competitive_analysis, risk_assessment, opportunity_identification, regulatory_compliance]
        recovery_type:
          type: string
          enum: [full, partial, point_in_time, incremental]
        node_language:
          type: string
          enum: [Python, JavaScript, TypeScript, Java, Go]
        management_action:
          type: string
          enum: [create, read, update, delete, execute, monitor]
        processing_type:
          type: string
          enum: [digital_archiving, cultural_analysis, preservation_planning, historical_research]
        model_type:
          type: string
        plugin_type:
          type: string
        validation_level:
          type: string
          enum: [basic, standard, strict]

    UnifiedOperationResponse:
      type: object
      properties:
        status:
          type: string
          enum: [success, error, pending]
        result:
          type: object
        workflow_id:
          type: string
        backup_id:
          type: string
        node_id:
          type: string
        training_id:
          type: string
        plugin_id:
          type: string
        validation_result:
          type: object
        analysis_report:
          type: object
        enhancement_result:
          type: object
        repair_report:
          type: object
        generation_output:
          type: object
        emergency_id:
          type: string
        recovery_id:
          type: string
        timestamp:
          type: string
          format: date-time
        execution_time:
          type: number

    ErrorResponse:
      type: object
      properties:
        error_code:
          type: string
        error_message:
          type: string
        error_details:
          type: object
        timestamp:
          type: string
          format: date-time
        request_id:
          type: string

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - BearerAuth: []
  - ApiKeyAuth: []