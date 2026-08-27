{
  "schema_version": "1.0",
  "name_for_human": "Coze全能智能自动化超级中枢",
  "name_for_model": "coze_unified_automation_center",
  "namespace": "coze_automation",
  "description_for_human": "完全自动化的智能处理系统 - 只需输入自然语言需求，系统自动完成工作流管理、插件生成、节点修复、AI增强、数据集成等所有操作。整合AutoPluginMaster + QuantumAutomationMaster + OmniAutoMaster全栈能力。",
  "description_for_model": "端到端自动化插件生成系统 - 输入描述即得完整插件，只需在结束点输入需求，全程自动完成的核心目标。核心能力：单一入口驱动、全自动逆向驱动、任意节点触发、零手动配置、全节点自愈、端到端插件生成、48项跨领域技术点整合。",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "https://api.coze-automation.com/v1/openapi.yaml",
    "is_user_authenticated": false
  },
  "logo_url": "https://api.coze-automation.com/logo.png",
  "contact_email": "support@coze-automation.com",
  "legal_info_url": "https://api.coze-automation.com/legal",
  "input_params": [
    {
      "name": "user_input",
      "type": "string",
      "required": true,
      "description": "请输入您的需求描述（系统自动识别并处理：工作流创建/插件开发/问题修复/AI分析/数据集成等所有操作）",
      "example": "创建一个数据备份工作流"
    },
    {
      "name": "auto_mode",
      "type": "boolean",
      "required": false,
      "description": "是否启用全自动模式",
      "default": true
    }
  ],
  "output_params": [
    {
      "name": "success",
      "type": "boolean",
      "description": "处理是否成功"
    },
    {
      "name": "detected_intent",
      "type": "string",
      "description": "检测到的用户意图类型"
    },
    {
      "name": "automated_tasks",
      "type": "array",
      "description": "自动执行的任务列表"
    },
    {
      "name": "generated_outputs",
      "type": "object",
      "description": "生成的各类输出结果"
    },
    {
      "name": "user_friendly_summary",
      "type": "string",
      "description": "用户友好的处理总结"
    }
  ]
}