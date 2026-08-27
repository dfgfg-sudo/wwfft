{
  "schema_version": "v1",
  "name_for_human": "企业工作流智能编排系统",
  "name_for_model": "enterprise_workflow_orchestrator",
  "description_for_human": "统一的企业级工作流管理、自动化执行和智能编排平台，集成30个核心功能模块",
  "description_for_model": "综合性的企业工作流管理插件，集成了工作流创建、执行、监控、修复、行业分析、紧急处理、数据训练等30个核心功能。支持多版本兼容、参数自动验证和智能错误处理。",
  "auth": {
    "type": "bearer"
  },
  "api": {
    "type": "openapi",
    "url": "https://api.enterprise-workflow.com/v1/openapi.yaml",
    "is_user_authenticated": true
  },
  "logo_url": "https://api.enterprise-workflow.com/icons/orchestrator.png",
  "contact_email": "support@enterprise-workflow.com",
  "legal_info_url": "https://enterprise-workflow.com/legal",
  "input_parameters": {
    "type": "object",
    "properties": {
      "operation_type": {
        "type": "string",
        "enum": [
          "activate_emergency",
          "ai_enhancement",
          "analyze_industry",
          "auto_repair",
          "backup_revert",
          "create_custom_node",
          "create_workflow",
          "delete_workflow",
          "execute_workflow",
          "feed_data",
          "generate_workflow",
          "get_data_connections",
          "get_workflow_by_id",
          "get_workflows",
          "process_automation",
          "process_luoyang_heritage",
          "repair_all_nodes",
          "train_model",
          "trigger_auto_plugin_workflow",
          "update_workflow",
          "validate_parameters"
        ],
        "description": "操作类型：选择要执行的具体功能"
      },
      "operation_config": {
        "type": "object",
        "description": "操作配置参数，根据不同的operation_type传入对应的参数对象"
      },
      "version": {
        "type": "string",
        "enum": ["v1.0", "v2.0", "v3.0"],
        "description": "功能版本号"
      },
      "async_execution": {
        "type": "boolean",
        "description": "是否异步执行"
      },
      "callback_url": {
        "type": "string",
        "format": "uri",
        "description": "异步回调URL"
      }
    },
    "required": ["operation_type", "operation_config"]
  }
}