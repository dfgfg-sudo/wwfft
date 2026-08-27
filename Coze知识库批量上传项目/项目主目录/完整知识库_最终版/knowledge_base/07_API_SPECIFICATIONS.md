# 📡 API规范文档

## 📋 概述

完整的OpenAPI规范文档，定义了智能自动化平台的所有API端点和数据结构。

---

## 🌐 OpenAPI规范

### 基础信息

| 属性 | 值 |
|------|------|
| **版本** | 3.0.3 |
| **标题** | Universal Automation API |
| **描述** | 全能智能自动化中枢API |
| **服务URL** | https://api.coze-automation.com/v1 |

### 完整OpenAPI定义

```yaml
openapi: 3.0.3
info:
  title: Universal Automation API
  description: 全能智能自动化中枢API - 提供工作流管理、插件开发、代码修复等完整自动化服务
  version: 1.0.0
  contact:
    name: Support
    email: support@auto-ai.com
    url: https://auto-ai.com/support

servers:
  - url: https://api.coze-automation.com/v1
    description: 生产环境
  - url: https://dev.api.coze-automation.com/v1
    description: 开发环境

paths:
  /workflow/create:
    post:
      summary: 创建工作流
      description: 根据用户需求创建新的工作流
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                requirement:
                  type: string
                  description: 用户需求描述
                template:
                  enum: [standard, advanced, custom]
                  default: standard
                schedule:
                  description: 定时调度表达式
              required: [requirement]
      responses:
        '200':
          description: 工作流创建成功
                  workflow_id: { type: string }
                  status: { type: string }
                  workflow_config: { type: object }
        '400':
          description: 请求参数错误

  /workflow/repair:
      summary: 修复工作流
      description: 检测并修复工作流配置中的问题
                repair_type:
                  enum: [auto, json, schema, url, params]
                  default: auto
                options:
                    validate_schema: { type: boolean, default: true }
                    fix_url_prefix: { type: boolean, default: true }
                    complete_params: { type: boolean, default: true }
              required: [workflow_id]
          description: 工作流修复成功
                  issues_found: { type: integer }
                  issues_fixed: { type: integer }
                  repaired_config: { type: object }

  /workflow/generate:
      summary: 生成工作流
      description: 根据自然语言需求自动生成工作流
                requirement: { type: string }
                template: { type: string }
                schedule: { type: string }
          description: 工作流生成成功

  /workflow/query:
    get:
      summary: 查询工作流列表
      description: 获取用户的工作流列表
      parameters:
        - name: page
          in: query
          type: integer
          default: 1
        - name: limit
          default: 10
        - name: status
          enum: [active, inactive, all]
          default: all
          description: 查询成功
                  workflows:
                    type: array
                    items:
                        name: { type: string }
                        created_at: { type: string }
                  total: { type: integer }
                  page: { type: integer }
                  limit: { type: integer }

  /tools/code-repair:
      summary: 代码修复
      description: 修复代码中的语法错误和逻辑问题
                code: { type: string }
                language:
                  enum: [python, javascript, java, c++, go, rust]
                fix_type:
                  enum: [auto, syntax, style, performance, security]
              required: [code]
          description: 代码修复成功
                  fixed_code: { type: string }
                  suggestions: { type: array, items: { type: string } }

  /tools/json-format:
      summary: JSON格式化
      description: 格式化JSON数据，修复语法错误
                json_string: { type: string }
                indent: { type: integer, default: 2 }
              required: [json_string]
          description: JSON格式化成功

  /tools/yaml-to-json:
      summary: YAML转JSON
      description: 将YAML格式转换为JSON格式
                yaml_string: { type: string }
              required: [yaml_string]
          description: 转换成功

  /tools/json-to-yaml:
      summary: JSON转YAML
      description: 将JSON格式转换为YAML格式

components:
  schemas:
    Workflow:
        description: { type: string }
        config: { type: object }
        status:
          enum: [active, inactive, draft]
        created_at: { type: string, format: date-time }
        updated_at: { type: string, format: date-time }
      required: [workflow_id, name, status]

    ErrorResponse:
        error: { type: string }
        message: { type: string }
        code: { type: integer }
        details: { type: object }
      required: [error, message, code]

  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.auto-ai.com/authorize
          tokenUrl: https://auth.auto-ai.com/token
          scopes:
            read: 读取权限
            write: 写入权限
            admin: 管理员权限

security:
  - ApiKeyAuth: []
```


## 📝 错误码说明

| 错误码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权访问 |
| 403 | Forbidden | 访问被拒绝 |
| 404 | Not Found | 资源未找到 |
| 409 | Conflict | 资源冲突 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |


## 📎 相关文档

- [Coze插件系统](01_COZE_PLUGIN_SYSTEM.md) - 插件开发框架
- [工作流自动化](06_WORKFLOW_AUTOMATION.md) - Coze工作流修复智能体
- [系统架构设计](10_SYSTEM_ARCHITECTURE.md) - 完整技术栈描述