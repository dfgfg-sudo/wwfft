{
  "plugin": {
    "id": "enterprise_workflow_orchestrator",
    "name": "企业工作流智能编排系统",
    "description": "统一的企业级工作流管理、自动化执行和智能编排平台",
    "version": "3.0.0",
    "author": "Enterprise Workflow Team",
    "homepage": "https://enterprise-workflow.com",
    "repository": "https://github.com/enterprise-workflow/ewio-plugin",
    "license": "Commercial",
    "tags": ["workflow", "automation", "ai", "enterprise", "orchestration"],
    "categories": ["productivity", "developer-tools", "business"],
    "icon": "https://api.enterprise-workflow.com/icons/orchestrator.png",
    "banner": "https://api.enterprise-workflow.com/banners/orchestrator-banner.png",
    "screenshots": [
      "https://api.enterprise-workflow.com/screenshots/dashboard.png",
      "https://api.enterprise-workflow.com/screenshots/workflow-designer.png",
      "https://api.enterprise-workflow.com/screenshots/analytics.png"
    ],
    "privacy_policy": "https://enterprise-workflow.com/privacy",
    "terms_of_service": "https://enterprise-workflow.com/terms",
    "support_email": "support@enterprise-workflow.com",
    "documentation": "https://docs.enterprise-workflow.com",
    "quick_start": "https://docs.enterprise-workflow.com/quick-start",
    "faq": "https://docs.enterprise-workflow.com/faq",
    "changelog": "https://docs.enterprise-workflow.com/changelog"
  },
  "capabilities": {
    "supports_async": true,
    "supports_streaming": false,
    "supports_attachments": true,
    "max_file_size": 10485760,
    "allowed_file_types": ["json", "yaml", "yml", "txt", "csv", "xml"],
    "rate_limit": {
      "requests_per_minute": 100,
      "burst_limit": 20
    },
    "memory_limit": "512MB",
    "timeout": 300
  },
  "integrations": {
    "coze": {
      "min_version": "1.0.0",
      "max_version": "2.0.0",
      "tested_versions": ["1.2.0", "1.5.0", "2.0.0"]
    },
    "apis": {
      "required": ["workflow-engine", "ai-services", "database"],
      "optional": ["monitoring", "logging", "cache"]
    }
  },
  "development": {
    "environment": {
      "node": ">=18.0.0",
      "npm": ">=9.0.0",
      "docker": ">=20.10.0"
    },
    "build_command": "npm run build",
    "test_command": "npm test",
    "deploy_command": "npm run deploy",
    "watch_command": "npm run watch"
  }
}