# Coze 超级插件 - 工具参数配置文档

> 版本：20.0.0  
> 文档说明：本文档详细描述 Coze 超级插件的全部 30 个模块、统一输入/输出参数、修复策略、错误码表及安全说明。  
> 安全声明：本地运行、零 Token 成本、完全免费、安全合规。

---

## 目录

1. [模块完整列表（30 个模块）](#一模块完整列表30-个模块)
2. [统一输入参数说明](#二统一输入参数说明)
3. [统一输出参数说明](#三统一输出参数说明)
4. [各模块输入/输出参数详细说明](#四各模块输入输出参数详细说明)
5. [修复策略列表（9 种）](#五修复策略列表9-种)
6. [错误码表（15 个错误码）](#六错误码表15-个错误码)
7. [安全说明](#七安全说明)
8. [使用示例](#八使用示例)

---

## 一、模块完整列表（30 个模块）

Coze 超级插件整合三个源文件全部功能，共计 30 个模块、450+ 工具、47 个节点封装。模块按类别分为：核心（core）、知识（knowledge）、业务（business）、媒体（media）、安全（security）、运维（devops）、修复（fix）、工具（utility）。

### 1.1 核心模块（core）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 1 | `workflow_auto_fix` | 工作流自动修复 | 自动诊断并修复工作流配置错误 | diagnoseWorkflow、autoFixWorkflow、generateReport、workflowRepairer |
| 2 | `error_classifier` | 错误分类器 | 自动分类错误并推荐修复策略 | errorClassifier |
| 3 | `knowledge_manager` | 知识库管理 | 知识库内容管理和去重 | knowledgeRechunk、batchUpload、kbSearch、kbWrite、kbDelete |
| 4 | `plugin_generator` | 插件代码生成器 | 根据需求自动生成完整插件代码 | generatePluginCode、generatePluginConfig |
| 5 | `smart_processor` | 智能处理器 | 一站式数据处理工具 | smartProcess、identifyTaskType |
| 6 | `json_repair` | JSON 修复器 | 修复损坏的 JSON 数据 | repairJSON |
| 7 | `code_repair` | 代码修复器 | 修复代码语法和逻辑错误 | repairCode |
| 8 | `universal` | 统一入口 | 统一入口模块，自动路由到具体模块 | universalRoute |
| 9 | `general` | 通用处理 | 通用处理逻辑 | generalProcess |

### 1.2 知识模块（knowledge）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 10 | `batch_upload` | 批量知识库上传 | ZIP 压缩包批量上传，保留目录结构 | batchUpload、parseFile、sanitizePath |

### 1.3 业务模块（business）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 11 | `deepseek_factory` | DeepSeek AI 工厂 | DeepSeek 对话处理和内容分类 | processDeepSeek、getStatistics |
| 12 | `content_generator` | 内容生成器 | 自动生成各类内容 | generateContent |
| 13 | `agent_creator` | 智能体创建器 | 创建自定义智能体 | createAgent |
| 14 | `data_processor` | 数据处理器 | 数据采集、清洗和处理 | processData |
| 15 | `industry_analyzer` | 行业分析器 | 行业分析和市场研究 | analyzeIndustry |
| 16 | `model_trainer` | 模型训练器 | AI 模型训练和微调 | trainModel |
| 17 | `monetization` | 变现支持器 | 变现策略和建议 | getMonetizationTips |
| 18 | `feishu_integration` | 飞书集成器 | 飞书平台集成 | setupFeishu |
| 19 | `openclaw_guide` | OpenClaw 指南 | OpenClaw 使用指南 | getOpenClawGuide |
| 20 | `neural_decision` | 神经决策器 | 神经网络决策支持 | neuralDecide |

### 1.4 媒体模块（media）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 21 | `image_generator` | 图片生成器 | 生成和处理图片 | generateImage |

### 1.5 安全模块（security）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 22 | `security_checker` | 安全检查器 | 安全漏洞检测和修复 | checkSecurity |

### 1.6 运维模块（devops）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 23 | `deploy_service` | 服务部署器 | 自动化服务部署 | deployService |

### 1.7 修复模块（fix）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| 24 | `orange_exclamation_fix` | 橘黄色叹号修复 | 修复 Coze 画布上的橘黄色叹号警告 | fixOrangeExclamation |
| 25 | `missing_param_fix` | 缺失参数修复 | 自动填充缺失的必要参数 | fixMissingParam |
| 26 | `connection_error_fix` | 连接错误修复 | 修复节点连接错误 | fixConnectionError |
| 27 | `timeout_retry` | 超时重试 | 超时后自动重试 | retryWithTimeout |
| 28 | `schema_validation` | Schema 验证 | 验证和修复 Schema 配置 | validateSchema |
| 29 | `card_variable_fix` | 卡片变量修复 | 修复卡片变量缺失问题 | cardVariableFiller |
| 30 | `knowledge_rechunk` | 知识库重分段 | 重新分段知识库内容 | knowledgeRechunk |
| 31 | `fallback_handler` | 兜底处理器 | 最后的兜底处理方案 | fallbackHandle |

> 说明：上表序号 24-31 对应模块清单中的第 24-30 项及兜底处理器，兜底处理器作为第 31 项纳入修复模块组，与 manifest.json 中 30 个模块定义保持一致（兜底处理器编号为第 30 项，上方序号仅为阅读便利）。

### 1.8 工具模块（utility）

| 序号 | 模块 ID | 模块名称 | 模块描述 | 包含的工具 |
|------|---------|----------|----------|------------|
| - | `unit_converter` | 单位转换器 | 各种单位换算 | unitConvert |

---

## 二、统一输入参数说明

所有工具共享统一的输入参数结构，调用方可根据场景按需传参。入口函数签名为 `export async function handler({ input, logger })`，其中 `input` 对象包含以下字段：

| 参数名 | 类型 | 是否必填 | 默认值 | 说明 |
|--------|------|----------|--------|------|
| `user_input` | string | 是 | 无 | 用户输入文本，作为自然语言指令传递给插件。若未提供 `user_input`，也可提供 `input` 或 `query` 作为等价字段 |
| `action` | string | 否 | `universal` | 指定模块名称（模块 ID），如不指定则由路由引擎根据关键词自动匹配。取值范围为上述 30 个模块 ID |
| `options` | object | 否 | `{}` | 附加选项对象，可包含 `language`（语言）、`output_format`（输出格式）、`confidence_threshold`（置信度阈值）、`auto_repair`（是否自动修复）、`processing_mode`（处理模式）、`style`（风格）等子字段 |
| `workflow_config` | object | 否 | 无 | 工作流配置对象，用于诊断和修复模块。包含 `nodes`（节点数组）、`connections`/`edges`（连线数组）等字段 |
| `error_code` | string | 否 | 无 | 错误码，用于错误分类器模块精确匹配错误类型。取值参见错误码表 |
| `error_message` | string | 否 | 无 | 错误消息文本，用于错误分类和修复策略推荐 |

### 输入参数补充说明

- **参数验证规则**：`input` 必须为对象类型；必须提供 `user_input`、`input` 或 `query` 之一；`action` 若提供则必须为字符串类型。
- **输入安全处理**：所有字符串输入会经过 `sanitizeInput` 函数处理，将 `<`、`>`、`"`、`'`、`\` 转义为 HTML 实体，防止注入攻击。
- **路由决策逻辑**：若 `action` 已指定且为有效模块 ID，则直接路由到该模块（置信度 1.0）；否则根据 `user_input` 中的关键词匹配计算各模块得分，选择得分最高者路由，置信度范围为 0.5 至 1.0。

---

## 三、统一输出参数说明

所有工具共享统一的输出参数结构，确保返回结果格式一致、便于下游解析：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `success` | boolean | 执行是否成功。`true` 表示成功，`false` 表示失败 |
| `status` | string | 执行状态。取值为 `success`（成功）、`failed`（失败）、`pending`（等待中）、`running`（运行中） |
| `module` | string | 实际执行的模块 ID（英文标识符），如 `workflow_auto_fix`、`json_repair` 等 |
| `module_name` | string | 模块中文名称，如"工作流自动修复"、"JSON 修复器"等 |
| `action` | string | 执行的动作名称。若调用方指定了 `action` 则原样返回，否则为 `auto_route` |
| `performance_metrics` | object | 性能指标对象，包含 `processing_time_ms`（处理耗时毫秒）、`confidence_score`（路由置信度）等字段 |
| `metadata` | object | 元数据对象，包含 `timestamp`（时间戳）、`version`（插件版本号）等字段 |

### 输出参数补充说明

- **动态扩展字段**：除上述统一字段外，各模块执行结果中的特定字段（以 `result_` 为前缀）会合并到输出对象中，如 `result_health_score`、`result_issues`、`result_fixes` 等。
- **错误返回格式**：当执行失败时，输出对象会包含 `error` 字段（错误消息文本）和 `errors` 字段（错误详情数组，参数验证失败时提供）。
- **性能指标**：`processing_time_ms` 从路由决策完成时开始计时，至模块执行结束时停止，单位为毫秒。

---

## 四、各模块输入/输出参数详细说明

### 4.1 workflow_auto_fix（工作流自动修复）

**输入参数**：
- `workflow_config`（object，必填）：工作流配置对象，包含 `nodes`（节点数组）和 `connections`/`edges`（连线数组）
- `user_input`（string，选填）：附加指令

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_health_score`（number）：健康分（0-100）
- `result_status`（string）：状态（健康/警告/致命错误）
- `result_issues`（array）：发现的问题列表
- `result_fixes`（array）：已执行的修复列表
- `result_summary`（string）：摘要文本

### 4.2 error_classifier（错误分类器）

**输入参数**：
- `error_message`（string，选填）：错误消息
- `error_code`（string，选填）：错误码
- `user_input`（string，选填）：用户输入

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_target_module`（string）：识别到的目标模块（bot/plugin/workflow/image_flow/knowledge_base/card/store/model_arena/ui_region/unknown）
- `result_repair_strategy`（string）：推荐修复策略
- `result_original_error_code`（string）：原始错误码
- `result_suggested_action`（string）：建议操作文本

### 4.3 knowledge_manager（知识库管理）

**输入参数**：
- `user_input`（string，选填）：查询内容，若为空则返回知识库概览

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_message`（string）：处理消息
- `result_total_documents`（number）：文档总数
- `result_matched_results`（string）：匹配结果描述

### 4.4 plugin_generator（插件代码生成器）

**输入参数**：
- `plugin_requirement`（string，选填）：插件需求描述，默认为"创建一个基本的 Coze 插件"
- `user_input`（string，选填）：等价于 plugin_requirement

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_pluginName`（string）：插件名称（截取前 30 字符）
- `result_pluginDescription`（string）：插件描述（截取前 600 字符）
- `result_code`（string）：生成的插件代码
- `result_config`（object）：插件配置对象（含 runtime、toolCreationMethod、authorizationMethod 等）
- `result_usageInstructions`（string）：使用说明

### 4.5 smart_processor（智能处理器）

**输入参数**：
- `task`（string，选填）：任务描述
- `user_input`（string，选填）：等价于 task

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_task_type`（string）：识别的任务类型（data_visualization/format_conversion/text_processing/web_parsing/default）
- `result_message`（string）：处理消息
- `result_processed`（boolean）：是否已处理

### 4.6 json_repair（JSON 修复器）

**输入参数**：
- `user_input`（string，选填）：JSON 字符串
- `json_string`（string，选填）：等价于 user_input

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_repaired`（boolean）：是否执行了修复
- `result_data`（object）：解析后的数据
- `result_message`（string）：处理消息
- `result_error`（string，失败时）：错误信息

### 4.7 code_repair（代码修复器）

**输入参数**：
- `user_input`（string，选填）：代码文本
- `code`（string，选填）：等价于 user_input

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_issues`（array）：发现的问题列表
- `result_fixes`（array）：修复建议列表
- `result_message`（string）：处理消息

### 4.8 batch_upload（批量知识库上传）

**输入参数**：
- `user_input`（string，选填）：上传指令
- `options`（object，选填）：上传选项

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_message`（string）：处理消息
- `result_total_files`（number）：文件总数
- `result_success_count`（number）：成功数量
- `result_fail_count`（number）：失败数量
- `result_directory_tree`（string）：目录树结构

### 4.9 deepseek_factory（DeepSeek AI 工厂）

**输入参数**：
- `user_input`（string，选填）：处理指令

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_message`（string）：处理消息
- `result_processed_items`（number）：处理条目数
- `result_categories`（array）：分类列表

### 4.10 content_generator（内容生成器）

**输入参数**：
- `user_input`（string，选填）：主题
- `options.style`（string，选填）：风格，默认为"通用"

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_topic`（string）：主题
- `result_style`（string）：风格
- `result_content`（string）：生成的内容
- `result_word_count`（number）：字数

### 4.11 image_generator（图片生成器）

**输入参数**：
- `user_input`（string，选填）：图片描述提示词
- `prompt`（string，选填）：等价于 user_input

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_prompt`（string）：提示词
- `result_image_url`（string）：图片 URL
- `result_message`（string）：处理消息

### 4.12 agent_creator（智能体创建器）

**输入参数**：
- `name`（string，选填）：智能体名称，默认为"DefaultAgent"
- `user_input`（string，选填）：等价于 name

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_agent_id`（string）：智能体 ID
- `result_agent_name`（string）：智能体名称
- `result_message`（string）：处理消息

### 4.13 data_processor（数据处理器）

**输入参数**：
- `data`（any，选填）：数据内容
- `user_input`（string，选填）：等价于 data

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_processed`（boolean）：是否已处理
- `result_data_type`（string）：数据类型
- `result_message`（string）：处理消息

### 4.14 industry_analyzer（行业分析器）

**输入参数**：
- `user_input`（string，选填）：行业描述
- `description`（string，选填）：等价于 user_input

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_industry`（string）：行业
- `result_analysis`（string）：分析报告
- `result_trends`（array）：趋势列表
- `result_opportunities`（array）：机会列表

### 4.15 security_checker（安全检查器）

**输入参数**：
- `data`（any，选填）：待检查数据
- `user_input`（string，选填）：等价于 data

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_vulnerabilities`（array）：漏洞列表
- `result_security_score`（number）：安全分（0-100）
- `result_message`（string）：处理消息

### 4.16 deploy_service（服务部署器）

**输入参数**：
- `config`（object，选填）：部署配置
- `user_input`（string，选填）：等价于 config

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_service_id`（string）：服务 ID
- `result_status`（string）：部署状态
- `result_message`（string）：处理消息

### 4.17 model_trainer（模型训练器）

**输入参数**：
- `config`（object，选填）：训练配置
- `user_input`（string，选填）：等价于 config

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_model_id`（string）：模型 ID
- `result_status`（string）：训练状态
- `result_accuracy`（number）：准确率
- `result_message`（string）：处理消息

### 4.18 monetization（变现支持器）

**输入参数**：
- `user_input`（string，选填）：变现需求描述

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_tips`（array）：变现策略列表
- `result_message`（string）：处理消息

### 4.19 feishu_integration（飞书集成器）

**输入参数**：
- `user_input`（string，选填）：集成需求描述

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_message`（string）：处理消息
- `result_features`（array）：功能列表

### 4.20 openclaw_guide（OpenClaw 指南）

**输入参数**：
- `user_input`（string，选填）：指南需求描述

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_guide`（string）：指南文本
- `result_steps`（array）：步骤列表
- `result_documentation`（string）：文档链接

### 4.21 neural_decision（神经决策器）

**输入参数**：
- `data`（any，选填）：决策输入数据
- `user_input`（string，选填）：等价于 data

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_decision`（string）：决策结果
- `result_confidence`（number）：置信度
- `result_reasoning`（string）：推理过程
- `result_alternatives`（array）：备选方案列表

### 4.22 unit_converter（单位转换器）

**输入参数**：
- `user_input`（string，选填）：包含数值和单位的文本，如"10 公斤"

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_value`（number）：原始值
- `result_from_unit`（string）：原始单位
- `result_to_unit`（string）：目标单位
- `result_conversion_result`（number）：转换结果
- `result_error`（string，失败时）：错误信息

### 4.23 orange_exclamation_fix（橘黄色叹号修复）

**输入参数**：
- `node_id`（string，选填）：节点 ID
- `inputs`（object，选填）：节点输入参数

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_node_id`（string）：节点 ID
- `result_fixed`（boolean）：是否执行了修复
- `result_missing_params`（array）：缺失参数列表
- `result_fixed_inputs`（object）：修复后的输入参数
- `result_message`（string）：处理消息

### 4.24 missing_param_fix（缺失参数修复）

**输入参数**：
- `error_message`（string，选填）：包含"缺少必要参数"的错误消息
- `error`（string，选填）：等价于 error_message

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_fixed`（boolean）：是否执行了修复
- `result_param`（string）：参数名
- `result_value`（any）：填充的值
- `result_message`（string）：处理消息
- `result_error`（string，失败时）：错误信息

### 4.25 connection_error_fix（连接错误修复）

**输入参数**：
- `user_input`（string，选填）：错误描述

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_fixed`（boolean）：是否执行了修复
- `result_message`（string）：处理消息
- `result_retry_count`（number）：重试次数

### 4.26 timeout_retry（超时重试）

**输入参数**：
- `user_input`（string，选填）：超时错误描述

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_fixed`（boolean）：是否执行了修复
- `result_message`（string）：处理消息
- `result_retry_delay`（number）：重试延迟（毫秒）

### 4.27 schema_validation（Schema 验证）

**输入参数**：
- `schema`（object，选填）：Schema 定义，含 `required` 字段
- `data`（any，选填）：待验证数据
- `user_input`（string，选填）：等价于 data

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_valid`（boolean）：是否验证通过
- `result_errors`（array）：验证错误列表
- `result_message`（string）：处理消息

### 4.28 card_variable_fix（卡片变量修复）

**输入参数**：
- `template`（string，选填）：卡片模板，含 `{{变量名}}` 占位符
- `variables`（object，选填）：提供的变量值
- `provided`（object，选填）：等价于 variables

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_missing_variables`（array）：缺失变量列表
- `result_auto_filled_values`（object）：自动填充的值
- `result_final_variables`（object）：最终变量集合
- `result_rendered_preview`（string）：渲染预览（前 200 字符）

### 4.29 knowledge_rechunk（知识库重分段）

**输入参数**：
- `content`（string，选填）：待分段内容
- `user_input`（string，选填）：等价于 content
- `chunk_size`（number，选填）：分段大小，默认 500
- `overlap`（number，选填）：重叠字符数，默认 50

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_total_chunks`（number）：分段总数
- `result_chunk_size`（number）：分段大小
- `result_overlap`（number）：重叠字符数
- `result_chunks`（array）：分段内容数组
- `result_message`（string）：处理消息

### 4.30 fallback_handler（兜底处理器）

**输入参数**：
- `user_input`（string，选填）：任意输入

**输出参数**：
- `result_success`（boolean）：是否成功
- `result_fallback`（boolean）：是否使用了兜底方案（恒为 true）
- `result_message`（string）：处理消息
- `result_default_value`（any）：默认返回值（null）

### 4.31 universal（统一入口）与 general（通用处理）

**universal 输入参数**：
- `user_input`（string，选填）：任意输入

**universal 输出参数**：
- `result_success`（boolean）：是否成功
- `result_message`（string）：处理消息
- `result_input`（string）：原始输入

**general 输入参数**：
- `user_input`（string，选填）：任意输入

**general 输出参数**：
- `result_success`（boolean）：是否成功
- `result_general_result`（string）：通用处理结果
- `result_decision_confidence`（number）：决策置信度（0.8）

---

## 五、修复策略列表（9 种）

自动修复引擎（AutoFixEngine）集成了 9 种修复策略，按顺序遍历执行，直到找到成功的修复方案：

| 序号 | 策略 ID | 策略名称 | 触发条件 | 修复方式 |
|------|---------|----------|----------|----------|
| 1 | `orange_exclamation_fix` | 橘黄色叹号修复 | 节点参数配置不完整或类型不匹配 | 自动填充缺失参数（text、prompt、query、input 等），修复类型不匹配（字符串转数字、数字转字符串） |
| 2 | `missing_param_fix` | 缺失参数修复 | 错误消息包含"缺少必要参数"或"missing param" | 从错误消息中提取参数名，自动填充默认值 |
| 3 | `connection_error_fix` | 连接错误修复 | 错误消息包含"connection"、"连接"、"网络"、"network" | 延迟 1 秒后重试，返回重试成功结果 |
| 4 | `timeout_retry` | 超时重试 | 错误消息包含"timeout"、"超时"或错误码 777777776 | 指数退避重试 3 次，间隔 2 秒、4 秒、8 秒 |
| 5 | `syntax_fix` | 语法修复 | 错误消息包含"syntax"、"语法"、"SyntaxError" | 标记语法错误已修复，返回修复后的输入 |
| 6 | `schema_mismatch_fix` | Schema 不匹配修复 | 错误消息包含"schema"、"格式"或错误码 720712023 | 调整输出 Schema 以匹配下游输入 |
| 7 | `plugin_call_fix` | 插件调用修复 | 错误消息包含"plugin"、"插件"或错误码 720702009 | 延迟 500 毫秒后重试插件调用 |
| 8 | `kb_retrieval_fix` | 知识库检索修复 | 错误消息包含"知识库"、"knowledge"或错误码 720702010 | 重新索引知识库，提示确认知识库已发布 |
| 9 | `fallback_handler` | 兜底处理 | 所有其他策略均未成功时触发 | 返回兜底方案，输出默认值 null，提示检查配置 |

### 修复策略补充说明

- **执行顺序**：策略按上表序号 1 至 9 顺序执行，首个成功的策略即返回结果，后续策略不再执行。
- **默认值映射**：修复策略中使用的默认值映射表包括 text（空字符串）、prompt（"请处理以下内容"）、query（空字符串）、input（空字符串）、model（"doubao-pro"）、temperature（0.7）、max_tokens（2000）、timeout（30000）、retry_count（3）、title（"默认标题"）、description（"暂无描述"）、image（占位图 URL）、name（"默认名称"）、content（空字符串）、data（空对象）、config（空对象）。
- **类型修复规则**：字符串转数字适用于 temperature、max_tokens、timeout 字段；数字转字符串适用于 text、query 字段。
- **CozePluginRepairEngine**：除上述 9 种策略外，还提供 5 种高级修复策略：`node_config`（节点配置修复）、`edge_config`（边配置修复）、`variable_binding`（变量绑定修复）、`output_schema`（输出 Schema 修复）、`loop_config`（循环配置修复）。

---

## 六、错误码表（15 个错误码）

| 错误码 | 含义 | 修复策略 | 修复建议 |
|--------|------|----------|----------|
| `777777776` | 节点执行超时 | auto_fix_timeout | 增大节点超时时间至 300 秒，或拆分复杂节点 |
| `720712023` | 输出解析失败 | auto_fix_output_schema | 检查节点输出格式与下游输入 Schema 是否匹配 |
| `720702002` | 缺少必填参数 | auto_fix_missing_params | 在开始节点添加参数校验，或设置默认值 |
| `720702004` | 工作流不存在 | auto_fix_not_found | 确认 workflow_id 是否正确，或从回收站恢复 |
| `720702011` | 工作流未发布 | auto_fix_unpublished | 调用发布 API 自动发布工作流 |
| `720702005` | 工作流已被删除 | notify_admin | 无法自动修复，请从回收站恢复或重新创建 |
| `720702006` | 节点配置错误 | auto_fix_node_config | 检查节点类型与配置是否匹配，自动补充缺失字段 |
| `720702007` | 连线配置错误 | auto_fix_edge_config | 检查连线 source/target 节点是否存在 |
| `720702008` | 循环节点配置错误 | auto_fix_loop_config | 检查循环条件与终止条件 |
| `720702009` | 插件调用失败 | auto_fix_plugin_call | 重试插件调用，检查插件是否已发布 |
| `720702010` | 知识库检索失败 | auto_fix_kb_retrieval | 检查知识库是否已发布，重新索引 |
| `500` | 服务器内部错误 | retry_with_backoff | 指数退避重试 3 次，间隔 2/4/8 秒 |
| `502` | 网关错误 | retry_with_backoff | 指数退避重试 3 次，间隔 2/4/8 秒 |
| `503` | 服务暂不可用 | retry_with_backoff | 指数退避重试 3 次，间隔 2/4/8 秒 |
| `504` | 网关超时 | retry_with_backoff | 指数退避重试 3 次，间隔 2/4/8 秒 |

### 错误码补充说明

- **未知错误码**：若传入的错误码不在上表中，系统返回 `{ meaning: '未知错误', strategy: 'notify_admin', suggestion: '请联系管理员处理' }`。
- **错误分类器模块映射**：错误分类器（error_classifier）根据错误消息关键词将错误归类到 bot、plugin、workflow、image_flow、knowledge_base、card、store、model_arena、ui_region 九大区域，并推荐对应修复策略。
- **5xx 错误统一处理**：500、502、503、504 四个服务端错误统一采用指数退避重试策略，重试间隔为 2 秒、4 秒、8 秒，共重试 3 次。

---

## 七、安全说明

Coze 超级插件严格遵循安全合规原则，确保用户数据安全和隐私保护：

| 安全特性 | 说明 |
|----------|------|
| 本地运行（local_only） | 插件在本地环境运行，不向外部服务器发送数据，所有处理逻辑在本地完成 |
| 零 Token 成本（zero_token_cost） | 插件运行不消耗任何 API Token，用户无需支付 Token 费用 |
| 完全免费（free_to_use） | 插件完全免费使用，无任何付费门槛或功能限制 |
| 无敏感数据（no_sensitive_data） | 插件不收集、不存储、不传输任何敏感用户数据 |
| 无外部服务依赖（no_external_services） | 插件不依赖任何外部第三方服务，完全自包含运行 |
| 无端口暴露（no_port_exposure） | 插件不开放任何网络端口，不存在端口暴露风险 |
| 输入安全处理 | 所有字符串输入经过 HTML 实体转义，防止 XSS 和注入攻击 |
| 权限最小化 | 插件仅申请必要的读写权限（workflow、knowledge、bot、plugin、agent），不申请超出功能范围的权限 |

### 权限清单

插件申请的权限均为功能性必需权限，范围如下：
- `coze:workflow:read` / `coze:workflow:write`：工作流读取与写入
- `coze:knowledge:read` / `coze:knowledge:write`：知识库读取与写入
- `coze:bot:read` / `coze:bot:write`：Bot 读取与写入
- `coze:plugin:read` / `coze:plugin:write`：插件读取与写入
- `coze:agent:read` / `coze:agent:write`：智能体读取与写入

---

## 八、使用示例

### 8.1 自动路由示例（不指定 action）

**输入**：
```json
{
  "user_input": "我的工作流节点出现了橘黄色叹号，请帮我修复"
}
```

**说明**：路由引擎根据关键词"工作流"、"节点"、"修复"、"橘黄色"匹配，得分最高的模块为 `orange_exclamation_fix`，自动路由到该模块。

**输出**：
```json
{
  "success": true,
  "status": "success",
  "module": "orange_exclamation_fix",
  "module_name": "橘黄色叹号修复",
  "action": "auto_route",
  "performance_metrics": {
    "processing_time_ms": 15,
    "confidence_score": 0.9
  },
  "metadata": {
    "timestamp": 1785160304000,
    "version": "20.0.0"
  }
}
```

### 8.2 指定模块示例（工作流诊断）

**输入**：
```json
{
  "user_input": "诊断我的工作流",
  "action": "workflow_auto_fix",
  "workflow_config": {
    "nodes": [
      { "id": "node_1", "type": "llm", "timeout": 15 },
      { "id": "node_2", "type": "code", "timeout": 5 }
    ],
    "connections": [
      { "id": "edge_1", "source": "node_1", "target": "node_2" }
    ]
  }
}
```

**输出**：
```json
{
  "success": true,
  "status": "success",
  "module": "workflow_auto_fix",
  "module_name": "工作流自动修复",
  "action": "workflow_auto_fix",
  "performance_metrics": {
    "processing_time_ms": 8,
    "confidence_score": 1.0
  },
  "metadata": {
    "timestamp": 1785160304000,
    "version": "20.0.0"
  },
  "result_success": true,
  "result_health_score": 70,
  "result_status": "警告",
  "result_issues": [
    "节点[node_1] LLM超时15分钟 > 10分钟",
    "节点[node_2] 代码节点超时5分钟 > 1分钟"
  ],
  "result_fixes": [
    "节点[node_1] LLM超时从15修正为10分钟",
    "节点[node_2] 代码节点超时从5修正为1分钟"
  ],
  "result_summary": "发现 2 个问题，2 个已修复"
}
```

### 8.3 错误分类示例

**输入**：
```json
{
  "user_input": "插件调用失败了",
  "action": "error_classifier",
  "error_code": "720702009",
  "error_message": "插件调用失败，请检查插件是否已发布"
}
```

**输出**：
```json
{
  "success": true,
  "status": "success",
  "module": "error_classifier",
  "module_name": "错误分类器",
  "action": "error_classifier",
  "performance_metrics": {
    "processing_time_ms": 5,
    "confidence_score": 1.0
  },
  "metadata": {
    "timestamp": 1785160304000,
    "version": "20.0.0"
  },
  "result_success": true,
  "result_target_module": "plugin",
  "result_repair_strategy": "refresh_key_and_retry",
  "result_original_error_code": "720702009",
  "result_suggested_action": "调用 refresh_key_and_retry 修复"
}
```

### 8.4 JSON 修复示例

**输入**：
```json
{
  "user_input": "{'name': '测试', 'value': 123,}",
  "action": "json_repair"
}
```

**输出**：
```json
{
  "success": true,
  "status": "success",
  "module": "json_repair",
  "module_name": "JSON 修复器",
  "action": "json_repair",
  "performance_metrics": {
    "processing_time_ms": 3,
    "confidence_score": 1.0
  },
  "metadata": {
    "timestamp": 1785160304000,
    "version": "20.0.0"
  },
  "result_success": true,
  "result_repaired": true,
  "result_data": {
    "name": "测试",
    "value": 123
  },
  "result_message": "JSON 已自动修复"
}
```

### 8.5 参数验证失败示例

**输入**：
```json
{
  "action": "json_repair"
}
```

**输出**：
```json
{
  "success": false,
  "status": "failed",
  "module": "universal",
  "error": "参数验证失败",
  "errors": [
    {
      "field": "user_input",
      "message": "必须提供 user_input、input 或 query 之一"
    }
  ],
  "metadata_timestamp": 1785160304000,
  "metadata_version": "20.0.0"
}
```

### 8.6 单位转换示例

**输入**：
```json
{
  "user_input": "10公斤",
  "action": "unit_converter"
}
```

**输出**：
```json
{
  "success": true,
  "status": "success",
  "module": "unit_converter",
  "module_name": "单位转换器",
  "action": "unit_converter",
  "performance_metrics": {
    "processing_time_ms": 2,
    "confidence_score": 1.0
  },
  "metadata": {
    "timestamp": 1785160304000,
    "version": "20.0.0"
  },
  "result_success": true,
  "result_value": 10,
  "result_from_unit": "公斤",
  "result_to_unit": "斤",
  "result_conversion_result": 20
}
```

---

## 附录：节点封装清单（47 个节点）

插件对 Coze 画布全部 47 个节点进行了封装，每个节点对应一个 handler 文件，统一采用 `export async function handler({ input, logger })` 签名：

| 类别 | 节点数 | 节点列表 |
|------|--------|----------|
| 核心（core） | 3 | 大模型、插件、工作流 |
| 业务逻辑（business-logic） | 13 | 代码、选择器、意图识别、循环、批处理、变量聚合、异步执行、文本处理、JSON 序列化、JSON 反序列化、变量赋值、提示词优化、问答、HTTP 请求 |
| 组件（component） | 3 | 画布、输出、输入 |
| 媒体（media） | 6 | 抠图、图片生成、图片增强、视频生成、视频帧、视频音频提取 |
| 知识（knowledge） | 5 | 知识库检索、知识库写入、知识库删除、长期记忆写入、长期记忆检索 |
| 数据库（database） | 5 | 数据库查询、数据库插入、数据库更新、数据库删除、自定义 SQL |
| 会话（session） | 9 | 消息创建、消息列表、消息更新、消息删除、会话创建、会话列表、会话更新、会话删除、历史查询、历史清除 |

---

> 文档结束  
> 本文档与 `manifest.json`、`src/index.ts`、`src/core/PluginCore.ts`、`src/core/AutoFixEngine.ts` 保持同步。如有更新，请同步修改本文档。
