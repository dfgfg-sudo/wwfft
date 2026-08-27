{
  "schema_version": "v2",
  "plugin_id": "com.aiworkflow.complete-platform",
  "plugin_namespace": "complete_ai_workflow_automation",
  "plugin_name": "CompleteAIWorkflowAutomationPlatform",
  "plugin_version": "1.0.0",
  "name_for_human": "全场景智能自动化超级中枢",
  "name_for_model": "quanchangjing_zhineng_zidonghua_chaoji_zhongshu",
  "description_for_human": "终极整合版｜神经决策+26核心功能｜行业分析+职业分类+场景处理+工作流自动化+错误修复｜洛阳非遗电商全链路支持｜全场景智能自动化系统｜支持行业分析、工作流生成、错误修复、非遗文化处理｜统一的全功能智能自动化平台，整合工作流管理、插件生成、AI处理、神经决策、IoT控制、错误修复等26+核心功能模块。支持自然语言生成、多模态内容创作、洛阳非遗电商全链路，100%解决参数验证错误。｜统一整合的智能自动化API中枢，支持多场景工作流自动化、数据集成与AI增强处理｜端到端自动化插件生成系统+量子级优化，支持AI训练、数据投喂、工作流自动化完整解决方案。严格遵循Coze官方规范，修复所有参数验证错误与URL前缀不一致问题。并融合个人成长财富知识库：新闻/地理/理财/国学/情商/经济周期/商业逻辑/科技前沿/AI创作/抖音正能量/识人术/读心术/心理学/为人处世/认知提升/财富流向/创业赚钱等全部内容。",
  "description_for_model": "全场景智能自动化超级中枢是终极整合的统一全功能工具，集神经决策与26大核心功能于一体，支持用户选择是否启用自动化处理。涵盖行业分析、职业分类、多场景智能处理、工作流自动化生成、AI多模态内容创作、IoT控制、错误修复与参数验证100%解决，并为洛阳非遗电商提供从分析到执行的全链路支持。同时内置了财富底层逻辑分析、经济周期预测、基金理财建议、地缘政治影响评估、AI替代与创造趋势、人情世故与识人读心策略等扩展知识模块，可用于回答关于金钱流向、宏观经济、商业思维、科技趋势、股市理财、法律法规、情商沟通等所有生存发展类问题。所有功能已整合为单一工具，支持灵活配置和自动化控制。严格遵循Coze官方规范，修复所有Invalid params、Inconsistent API URL prefix、API response schema must be json object/array错误。本插件为最终版，合并了全部历史版本的代码与描述，无任何遗漏。",
  "auth": {
    "type": "bearer"
  },
  "api": {
    "type": "openapi",
    "url": "https://api.quanchangjing.com/v1/openapi.yaml",
    "is_user_authenticated": true
  },
  "logo_url": "https://api.quanchangjing.com/logo.png",
  "contact_email": "support@quanchangjing.com",
  "legal_info_url": "https://www.quanchangjing.com/legal",
  "http_client": {
    "timeout_seconds": 60,
    "retry_config": {
      "strategy": "exponential_backoff",
      "max_attempts": 3,
      "base_interval_seconds": 2
    }
  },
  "input_parameters": {
    "type": "object",
    "properties": {
      "operation_type": {
        "type": "string",
        "enum": [
          "activate_emergency", "ai_enhancement", "analyze_industry", "auto_repair",
          "backup_revert", "create_custom_node", "create_workflow", "delete_workflow",
          "execute_workflow", "feed_data", "generate_workflow", "get_data_connections",
          "get_workflow_by_id", "get_workflows", "process_automation", "process_luoyang_heritage",
          "repair_all_nodes", "train_model", "trigger_auto_plugin_workflow", "update_workflow",
          "validate_parameters", "emergency_activation", "workflow_management", "data_feeding",
          "automated_generation", "data_connection_management", "cultural_heritage_processing",
          "model_training", "plugin_automation", "parameter_validation"
        ],
        "description": "操作类型：选择要执行的具体功能"
      },
      "operation_config": {
        "type": "object",
        "description": "操作配置参数，根据不同的operation_type传入对应的参数对象",
        "properties": {
          "emergency_config": {
            "type": "object",
            "properties": {
              "emergency_level": { "type": "string", "enum": ["low","medium","high","critical","level1","level2","level3","level4"] },
              "activation_reason": { "type": "string" },
              "auto_recovery": { "type": "boolean" },
              "recovery_strategy": { "type": "string", "enum": ["immediate","gradual","manual"] },
              "notification_contacts": { "type": "array", "items": { "type": "string", "format": "email" } }
            }
          },
          "ai_enhancement_config": {
            "type": "object",
            "properties": {
              "input_data": { "type": "string" },
              "enhancement_type": { "type": "string", "enum": ["cleaning","enrichment","completion","quality_improvement","semantic_enrichment","feature_extraction","pattern_recognition","anomaly_detection"] },
              "output_format": { "type": "string", "enum": ["json","xml","csv","text"] },
              "batch_data": { "type": "array", "items": { "type": "object" } },
              "options": { "type": "object" }
            }
          },
          "workflow_config": {
            "type": "object",
            "properties": {
              "workflow_id": { "type": "string" },
              "workflow_name": { "type": "string" },
              "description": { "type": "string" },
              "nodes": { "type": "array", "items": { "type": "object" } },
              "triggers": { "type": "array", "items": { "type": "object" } },
              "requirement_description": { "type": "string" },
              "business_domain": { "type": "string", "enum": ["ecommerce","industry","programming","finance","healthcare","manufacturing","retail","education"] },
              "execution_parameters": { "type": "object" },
              "update_operations": { "type": "array", "items": { "type": "object" } },
              "complexity_level": { "type": "string", "enum": ["simple","medium","complex"] },
              "validation_strictness": { "type": "string", "enum": ["relaxed","standard","strict"] },
              "monitoring_level": { "type": "string", "enum": ["basic","detailed","verbose"] },
              "result_format": { "type": "string", "enum": ["summary","detailed","raw"] },
              "version_comment": { "type": "string" }
            }
          },
          "repair_config": {
            "type": "object",
            "properties": {
              "repair_type": { "type": "string", "enum": ["system","network","database","application","performance"] },
              "diagnosis_level": { "type": "string", "enum": ["quick","standard","comprehensive","deep","predictive"] },
              "diagnosis_mode": { "type": "string", "enum": ["quick","deep","predictive"] },
              "auto_execute": { "type": "boolean" },
              "repair_strategy": { "type": "string", "enum": ["auto","semi_auto","manual_approval"] },
              "backup_before_repair": { "type": "boolean" },
              "repair_scope": { "type": "string", "enum": ["configuration","logic","dependencies","all"] },
              "target_components": { "type": "array", "items": { "type": "string" } }
            }
          },
          "backup_config": {
            "type": "object",
            "properties": {
              "backup_id": { "type": "string" },
              "revert_scope": { "type": "string", "enum": ["full","partial","data_only"] },
              "revert_type": { "type": "string", "enum": ["full","incremental","selective","point_in_time"] },
              "confirmation_required": { "type": "boolean" },
              "target_components": { "type": "array", "items": { "type": "string" } },
              "preview_changes": { "type": "boolean" },
              "rollback_plan": { "type": "string" },
              "conflict_resolution": { "type": "string", "enum": ["overwrite","merge","skip"] }
            }
          },
          "custom_node_config": {
            "type": "object",
            "properties": {
              "node_type": { "type": "string", "enum": ["code","plugin","metadata"] },
              "programming_language": { "type": "string", "enum": ["python","javascript","typescript","java","go"] },
              "node_name": { "type": "string" },
              "code_content": { "type": "string" },
              "dependencies": { "type": "array", "items": { "type": "string" } },
              "configuration": { "type": "object" },
              "description": { "type": "string" }
            }
          },
          "industry_config": {
            "type": "object",
            "properties": {
              "industry_name": { "type": "string" },
              "analysis_depth": { "type": "string", "enum": ["basic","standard","comprehensive"] },
              "analysis_type": { "type": "string", "enum": ["classification","trends","competitive","risk","market_trends","opportunity_identification","regulatory_compliance","economic_cycle","wealth_flow"] },
              "industry_type": { "type": "string", "enum": ["manufacturing","retail","healthcare","finance","education"] },
              "time_period": { "type": "string" },
              "include_trends": { "type": "boolean" },
              "include_forecast": { "type": "boolean" },
              "region": { "type": "string" },
              "data_sources": { "type": "array", "items": { "type": "string" } },
              "geographic_scope": { "type": "string" },
              "forecast_period": { "type": "string" },
              "comparison_metrics": { "type": "array", "items": { "type": "string" } }
            }
          },
          "training_config": {
            "type": "object",
            "properties": {
              "training_data": { "type": "string" },
              "training_dataset": { "type": "string" },
              "model_type": { "type": "string", "enum": ["classification","regression","clustering","nlp"] },
              "model_target": { "type": "string" },
              "data_format": { "type": "string", "enum": ["json","csv","text","image","audio","video","tabular","time_series"] },
              "validation_split": { "type": "number", "minimum": 0, "maximum": 1 },
              "training_parameters": { "type": "object" },
              "preprocessing": { "type": "object" },
              "data_quality_check": { "type": "boolean" },
              "hyperparameter_tuning": { "type": "boolean" }
            }
          },
          "heritage_config": {
            "type": "object",
            "properties": {
              "heritage_type": { "type": "string", "enum": ["intangible","tangible","cultural_practice"] },
              "heritage_category": { "type": "string", "enum": ["traditional_craft","performing_arts","rituals","oral_traditions"] },
              "action_type": { "type": "string", "enum": ["query","register","update","preserve"] },
              "processing_mode": { "type": "string", "enum": ["cataloging","digital_preservation","public_display","research","digital_archiving","cultural_analysis","preservation_planning","historical_research"] },
              "heritage_data": { "type": "object" },
              "cultural_context": { "type": "object" },
              "preservation_level": { "type": "string", "enum": ["basic","standard","premium"] },
              "location": { "type": "string" },
              "digital_assets": { "type": "array", "items": { "type": "string" } }
            }
          },
          "automation_config": {
            "type": "object",
            "properties": {
              "operation_mode": { "type": "string", "enum": ["industry_analysis","workflow_generation","auto_repair","luoyang_heritage","custom"] },
              "input_data": { "type": "object" },
              "input_parameters": { "type": "object" },
              "processing_level": { "type": "string", "enum": ["basic","advanced","comprehensive"] },
              "optimization_level": { "type": "string", "enum": ["standard","optimized","max_performance"] },
              "error_handling": { "type": "string", "enum": ["strict","lenient","adaptive"] },
              "output_format": { "type": "string" },
              "parallel_processing": { "type": "boolean" }
            }
          },
          "validation_config": {
            "type": "object",
            "properties": {
              "parameters_to_validate": { "type": "object" },
              "validation_rules": { "type": "object" },
              "strict_mode": { "type": "boolean" },
              "context": { "type": "object" }
            }
          },
          "plugin_config": {
            "type": "object",
            "properties": {
              "plugin_description": { "type": "string" },
              "trigger_conditions": { "type": "object" },
              "self_healing_enabled": { "type": "boolean" },
              "execution_priority": { "type": "string", "enum": ["low","normal","high","critical"] },
              "node_types": { "type": "array", "items": { "type": "string" } }
            }
          },
          "connection_config": {
            "type": "object",
            "properties": {
              "connection_type": { "type": "string", "enum": ["all","database","api","file","streaming"] },
              "status_filter": { "type": "string", "enum": ["all","active","inactive","error"] },
              "include_details": { "type": "boolean" }
            }
          },
          "query_config": {
            "type": "object",
            "properties": {
              "page_number": { "type": "integer", "minimum": 1 },
              "page_size": { "type": "integer", "minimum": 1, "maximum": 100 },
              "filter_by_status": { "type": "string", "enum": ["all","active","inactive","draft"] },
              "sort_by": { "type": "string", "enum": ["name","created_date","modified_date"] },
              "include_execution_history": { "type": "boolean" },
              "include_node_details": { "type": "boolean" }
            }
          }
        }
      },
      "version": { "type": "string", "enum": ["v1.0","v2.0","v3.0","v10.1.0"], "default": "v1.0" },
      "async_execution": { "type": "boolean", "default": false },
      "callback_url": { "type": "string", "format": "uri" },
      "automation_enabled": { "type": "boolean", "default": true, "description": "是否启用自动化处理" }
    },
    "required": ["operation_type", "operation_config"]
  },
  "plugin_tools": [
    {
      "tool_id": "T001",
      "tool_name": "CompleteAIWorkflowAutomationPlatform",
      "tool_version": "1.0.0",
      "tool_description": "统一AI工作流自动化平台，集成所有操作模式。",
      "input_parameters": [
        {
          "name": "operation_mode",
          "type": "string",
          "required": true,
          "description": "操作模式选择",
          "enum": [
            "emergency_activation", "ai_enhancement", "industry_analysis",
            "auto_repair", "backup_recovery", "custom_node_creation",
            "workflow_management", "data_feeding", "automated_generation",
            "data_connection_management", "process_automation",
            "cultural_heritage_processing", "model_training",
            "plugin_automation", "parameter_validation"
          ]
        },
        { "name": "input_data", "type": "object", "required": true, "description": "输入数据" },
        { "name": "workflow_id", "type": "string", "required": false, "description": "工作流ID" },
        { "name": "backup_id", "type": "string", "required": false, "description": "备份ID" },
        { "name": "node_config", "type": "object", "required": false, "description": "节点配置" },
        { "name": "training_data", "type": "array", "required": false, "description": "训练数据" },
        { "name": "plugin_description", "type": "string", "required": false, "description": "插件描述" },
        { "name": "validation_rules", "type": "object", "required": false, "description": "验证规则" },
        { "name": "industry_type", "type": "string", "required": false, "description": "行业类型" },
        { "name": "heritage_category", "type": "string", "required": false, "description": "文化遗产类别" },
        { "name": "repair_level", "type": "string", "required": false, "enum": ["low","medium","high","critical"], "description": "修复级别" },
        { "name": "generation_template", "type": "string", "required": false, "description": "生成模板" },
        { "name": "emergency_type", "type": "string", "required": false, "enum": ["system_failure","security_breach","performance_degradation","data_corruption"], "description": "紧急类型" },
        { "name": "severity", "type": "string", "required": false, "enum": ["low","medium","high","critical"], "description": "严重级" },
        { "name": "data_type", "type": "string", "required": false, "enum": ["text","image","audio","video","tabular","time_series"], "description": "数据类型" },
        { "name": "enhancement_type", "type": "string", "required": false, "enum": ["semantic_enrichment","quality_improvement","feature_extraction","pattern_recognition","anomaly_detection"], "description": "增强类型" },
        { "name": "analysis_type", "type": "string", "required": false, "enum": ["market_trends","competitive_analysis","risk_assessment","opportunity_identification","regulatory_compliance"], "description": "分析类型" },
        { "name": "recovery_type", "type": "string", "required": false, "enum": ["full","partial","point_in_time","incremental"], "description": "恢复类型" },
        { "name": "node_language", "type": "string", "required": false, "enum": ["Python","JavaScript","TypeScript","Java","Go"], "description": "节点语言" },
        { "name": "management_action", "type": "string", "required": false, "enum": ["create","read","update","delete","execute","monitor"], "description": "管理动作" },
        { "name": "processing_type", "type": "string", "required": false, "enum": ["digital_archiving","cultural_analysis","preservation_planning","historical_research"], "description": "处理类型" }
      ],
      "output_parameters": [
        { "name": "status", "type": "string", "description": "操作状态" },
        { "name": "result", "type": "object", "description": "操作结果" },
        { "name": "workflow_id", "type": "string", "description": "工作流ID" },
        { "name": "backup_id", "type": "string", "description": "备份ID" },
        { "name": "node_id", "type": "string", "description": "节点ID" },
        { "name": "training_id", "type": "string", "description": "训练ID" },
        { "name": "plugin_id", "type": "string", "description": "插件ID" },
        { "name": "validation_result", "type": "object", "description": "验证结果" },
        { "name": "analysis_report", "type": "object", "description": "分析报告" },
        { "name": "enhancement_result", "type": "object", "description": "增强结果" },
        { "name": "repair_report", "type": "object", "description": "修复报告" },
        { "name": "generation_output", "type": "object", "description": "生成输出" },
        { "name": "emergency_id", "type": "string", "description": "紧急ID" },
        { "name": "recovery_id", "type": "string", "description": "恢复ID" },
        { "name": "timestamp", "type": "string", "description": "时间戳" },
        { "name": "execution_time", "type": "number", "description": "执行时间" },
        { "name": "error_details", "type": "object", "description": "错误详情" }
      ],
      "service_status": "online",
      "debug_status": "enabled",
      "agent_reference_count": 0,
      "created_time": "2026-06-28T00:00:00Z"
    }
  ],
  "plugin_config": {
    "api_endpoints": {
      "base_url": "https://api.quanchangjing.com/v1",
      "execute_operation": "/operations/execute"
    },
    "authentication": {
      "type": "bearer_token",
      "required": true
    },
    "rate_limits": {
      "requests_per_minute": 100,
      "requests_per_hour": 1000
    },
    "timeout": {
      "request_timeout": 30000,
      "connection_timeout": 10000
    }
  }
}