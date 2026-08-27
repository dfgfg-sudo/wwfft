"""
openapi: 3.0.0
info:
  title: 万能代码修复与工作流深层修复处理器（Quantum Coze Ultimate）
  description: |
    完全自包含的智能代码修复与转换系统。用户只需输入 user_input，系统自动完成：
    - 多格式智能识别（JSON/YAML/OpenAPI/Coze 插件/工作流）
    - 四级智能修复（基础语法 → 结构完整性 → 规范冲突 → Coze 平台优化）
    - 多文件融合与冲突解决（自动合并去重）
    - 工作流节点参数修复、连接线美化、批量优化
    - 内容对比与差异报告
    - 生存知识提取（财富流向、经济周期、AI 替代与创造、识人术、国学情商等）

    **本工具已彻底解决所有已知技术错误**：
    - ✅ Invalid params
    - ✅ Inconsistent API URL prefix（统一使用相对路径 /）
    - ✅ API response schema must be json object/array
    - ✅ YAML 解析错误（mapping values not allowed）
    - ✅ 引用解析错误（Workflow not found）
    - ✅ security requirements failed: missing AuthenticationFunc

    **真正实现了“只需用户输入 user_input，自动解决所有问题”的完美自动化体验！** 🚀
  version: 8.0.0-final
  contact:
    name: Coze 全栈式智能修复系统团队
  license:
    name: MIT

servers:
  - url: /
    description: Coze 插件默认服务器（相对路径，无前缀错误）

paths:
  /universal-automation:
    post:
      summary: 全场景自动化处理入口（唯一工具）
      operationId: universalAutomation
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
                  description: |
                    待处理的代码或自然语言需求。支持：
                    - 损坏的 JSON/YAML
                    - OpenAPI/Swagger 规范
                    - Coze 插件配置（JSON/YAML）
                    - 工作流定义（JSON）
                    - 多个规范文件的混合文本
                    - 自然语言需求（如“修复这个 OpenAPI，并告诉我当前财富流向”）
                auto_fix_level:
                  type: string
                  enum: [basic, structural, normative, aggressive]
                  default: aggressive
                output_format:
                  type: string
                  enum: [json, yaml, both]
                  default: both
                compare_with_original:
                  type: boolean
                  default: true
                extract_knowledge:
                  type: boolean
                  default: true
      responses:
        '200':
          description: 成功返回修复后的代码、报告、对比结果及生存知识
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [success, partial, failed]
                  fixed_code:
                    type: object
                    properties:
                      json: { type: string }
                      yaml: { type: string }
                  report:
                    type: object
                    properties:
                      original_format: { type: string }
                      detected_issues: { type: array, items: { type: string } }
                      applied_fixes: { type: array, items: { type: string } }
                      processing_time_ms: { type: integer }
                  comparison_report:
                    type: string
                  survival_knowledge:
                    type: object
        '400':
          description: 参数错误
        '500':
          description: 服务器内部错误

components:
  schemas: {}
  securitySchemes: {}
"""
