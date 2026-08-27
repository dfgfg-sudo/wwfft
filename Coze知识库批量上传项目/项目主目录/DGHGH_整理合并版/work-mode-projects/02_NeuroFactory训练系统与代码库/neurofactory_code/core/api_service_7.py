{
  "schema_version": "v1",
  "name_for_human": "终极统一智能自动化超级中枢",
  "name_for_model": "UnifiedIntelligentAutomationSuperHub",
  "description_for_human": "全插件深度融合版｜58项核心功能统一调度｜智能路由决策｜跨工作流协同｜全链路监控",
  "description_for_model": "企业级统一整合的智能自动化API中枢，支持多场景工作流自动化、数据集成与AI增强处理。整合AutoPluginMaster + QuantumAutomationMaster + OmniAutoMaster + 企业工作流智能编排系统全栈能力。",
  "auth": {
    "type": "service_http",
    "authorization_type": "bearer",
    "verification_tokens": {
      "coze": "{{secrets.COZE_VERIFICATION_TOKEN}}"
    }
  },
  "api": {
    "type": "openapi",
    "url": "https://api.unified-automation.com/v15/openapi.yaml",
    "has_user_authentication": false
  },
  "logo_url": "https://docs.unified-automation.com/logo.png",
  "contact_email": "enterprise-support@unified-automation.com",
  "legal_info_url": "https://docs.unified-automation.com/legal",
  "http_authorization_header": "Bearer",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_input": {
        "type": "string",
        "description": "用户输入的需求描述或指令"
      },
      "enable_automation": {
        "type": "boolean",
        "default": true,
        "description": "是否启用自动化处理"
      },
      "automation_level": {
        "type": "string",
        "enum": ["basic", "advanced", "full"],
        "default": "full",
        "description": "自动化处理级别"
      }
    },
    "required": ["user_input"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "task_id": {"type": "string"},
      "execution_summary": {"type": "object"},
      "results": {"type": "object"}
    },
    "required": ["success", "task_id"]
  }
}