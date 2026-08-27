# Coze终极插件套件 - 完整合并文档

## 目录概览

本文档整合了所有相关的md文件内容，包含Coze终极插件套件的完整功能说明、使用指南、参数配置、错误修复等信息。

---

## 一、完整参数说明

### 1. 输入参数 (input_schema)

#### 一级参数
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `action` | String | 否 | `"universal"` | 操作类型 |
| `user_input` | String | 是 | - | 用户输入内容 |
| `options` | Object | 否 | - | 扩展配置选项 |

#### options 子参数
| 参数名 | 类型 | 默认值 | 枚举值 | 描述 |
|--------|------|--------|--------|------|
| `language` | String | `"zh_CN"` | zh_CN/en_US/ja_JP/ko_KR | 语言设置 |
| `output_format` | String | `"json"` | json/text/html | 输出格式 |
| `confidence_threshold` | Number | `0.6` | 0-1 | 置信度阈值 |
| `auto_repair` | Boolean | `true` | true/false | 是否自动修复 |
| `processing_mode` | String | `"standard"` | simple/standard/advanced | 处理模式 |
| `enable_automation` | Boolean | `true` | true/false | 是否启用自动化 |

### 2. 输出参数 (output_schema)

#### 一级参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `success` | Boolean | 是 | 请求是否成功 |
| `status` | String | 是 | 执行状态 |
| `module` | String | 是 | 处理的模块名称 |
| `module_name` | String | 否 | 模块显示名称 |
| `module_description` | String | 否 | 模块描述 |
| `detected_intent` | String | 否 | 检测到的用户意图 |
| `action` | String | 否 | 执行的具体操作 |
| `result` | Object | 是 | 实际执行结果 |
| `performance_metrics` | Object | 否 | 性能指标 |
| `next_actions` | Array | 否 | 建议的下一步操作 |
| `errors_fixed` | Array | 否 | 已修复的错误列表 |
| `metadata` | Object | 否 | 元数据信息 |


## 二、支持的模块列表 (21个)

| 模块ID | 模块名称 | 功能描述 |
|--------|----------|----------|
| universal | 统一入口 | 智能路由统一入口 |
| workflow | 工作流自动化 | 工作流创建、修复、执行 |
| plugin | 插件开发 | 插件自动创建与测试 |
| json_fix | JSON修复 | JSON数据修复与格式化 |
| code_fix | 代码修复 | 代码智能修复 |
| ai_training | AI训练 | AI模型训练与数据处理 |
| neural_decision | 神经决策系统 | 智能决策支持 |
| multimedia | 多媒体处理 | 多媒体内容处理 |
| industry_analysis | 行业分析 | 行业数据分析 |
| data_processing | 数据处理 | 数据处理工具 |
| error_fix | 错误修复 | 自动错误检测与修复 |
| deepseek | DeepSeek处理 | DeepSeek对话数据处理 |
| smart_agent | 智能代理 | 智能代理服务 |
| content_creation | 内容创作 | 内容自动生成 |
| monetization | 变现赚钱 | 收入来源分析 |
| devops | 部署运维 | 自动化部署 |
| openclaw | OpenClaw集成 | OpenClaw工具集成 |
| security_compliance | 安全合规 | 安全合规检查 |
| luoyang_heritage | 洛阳非遗 | 非遗保护支持 |
| feishu | 飞书集成 | 飞书助手搭建 |
| unit_conversion | 单位换算 | 公斤斤换算等 |
| general | 通用处理 | 通用工具处理 |


## 三、工具列表 (226-242个工具)

### 基础工具
| 工具名称 | 描述 | 端点 | 方法 |
|---------|------|------|------|
| universal_execute | 统一入口 | /execute | POST |
| validate_parameters | 参数验证 | /validate | POST |
| health_check | 健康检查 | /health | GET |

### 工作流工具
| workflow_create | 创建工作流 | /workflow/create | POST |
| workflow_repair | 修复工作流 | /workflow/repair | POST |
| workflow_generate | 生成工作流 | /workflow/generate | POST |
| query_workflows | 查询工作流 | /workflow/query | GET |
| workflow_execute | 执行工作流 | /workflow/execute | POST |
| workflow_batch_generate | 批量生成 | /workflow/batch | POST |
| workflow_visual_build | 可视化构建 | /workflow/visual | POST |
| workflow_validate | 验证工作流 | /workflow/validate | POST |
| workflow_optimize | 优化工作流 | /workflow/optimize | POST |
| workflow_monitor | 监控工作流 | /workflow/monitor | GET |
| workflow_schedule | 定时调度 | /workflow/schedule | POST |
| workflow_clone | 克隆工作流 | /workflow/clone | POST |
| workflow_share | 分享工作流 | /workflow/share | POST |

### 代码工具
| code_repair | 代码修复 | /tools/code-repair | POST |
| json_format | JSON格式化 | /tools/json-format | POST |
| yaml_to_json | YAML转JSON | /tools/yaml-to-json | POST |
| json_to_yaml | JSON转YAML | /tools/json-to-yaml | POST |

### AI训练工具
| ai_training | AI训练 | /ai/training | POST |
| ai_model_trainer | 模型训练器 | /ai/model-trainer | POST |
| ai_enhancement | AI增强 | /ai/enhancement | POST |
| lora_finetune | LoRA微调 | /ai/lora | POST |
| data_feeding | 数据喂入 | /ai/feed | POST |
| gpu_scheduling | GPU调度 | /ai/gpu | POST |
| model_optimize | 模型优化 | /ai/optimize | POST |
| dataset_prepare | 数据集准备 | /ai/dataset | POST |
| hyperparameter_tune | 超参数调优 | /ai/tune | POST |
| model_evaluate | 模型评估 | /ai/evaluate | POST |
| model_deploy | 模型部署 | /ai/deploy | POST |
| model_registry | 模型注册 | /ai/registry | POST |

### DeepSeek工具
| deepseek_parse | DeepSeek解析 | /deepseek/parse | POST |
| extract_code_blocks | 提取代码块 | /code/extract | POST |
| classify_conversations | 对话分类 | /deepseek/classify | POST |
| search_conversations | 搜索对话 | /deepseek/search | POST |
| get_statistics | 统计信息 | /deepseek/statistics | GET |
| merge_all_data | 合并数据 | /deepseek/merge | POST |
| export_formats | 多格式导出 | /deepseek/export | POST |


## 四、错误代码表

| 错误代码 | 描述 | 解决方案 | 自动修复 |
|---------|------|---------|--------|
| err_invalid_params | 参数验证错误 | 检查输入参数格式 | ✅ |
| err_api_prefix | API URL前缀不一致 | 统一使用/api/v1前缀 | ✅ |
| err_json_schema | JSON Schema错误 | 检查JSON格式 | ✅ |
| err_workflow | 工作流执行错误 | 检查工作流配置 | ✅ |
| err_plugin | 插件执行错误 | 检查插件代码 | ✅ |
| err_export_function | 函数导出错误 | 重命名入口函数 | ✅ |
| err_dependency | 依赖错误 | 移除非原生模块 | ✅ |
| err_type_conflict | 类型冲突 | 重命名冲突类型 | ✅ |
| err_path | 路径错误 | 修复URL重复片段 | ✅ |
| err_auth | 认证错误 | 检查环境变量 | ❌ |
| err_rate_limit | 限流错误 | 等待后重试 | ✅ |

### 扩展错误码表

| 错误码 | 说明 | 自动修复策略 | 修复建议 |
|--------|------|-------------|----------|
| 777777776 | 节点执行超时 | auto_fix_timeout | 增大超时阈值或拆分节点 |
| 720712023 | 输出解析失败 | auto_fix_output_schema | 检查输出格式与Schema匹配 |
| 720702002 | 缺少必填参数 | auto_fix_missing_params | 添加参数或使用默认值 |
| 720702004 | 工作流不存在 | auto_fix_not_found | 检查ID或从回收站恢复 |
| 720702011 | 工作流未发布 | auto_fix_unpublished | 自动发布工作流 |
| 500 | 服务器内部错误 | retry_with_backoff | 指数退避重试 |
| 502 | 网关错误 | retry_with_backoff | 指数退避重试 |
| 503 | 服务完全不可用 | retry_with_backoff | 指数退避重试 |
| 504 | 网关超时 | retry_with_backoff | 指数退避重试 |


## 五、DeepSeek历史对话整理

### 数据统计
| 项目 | 数量 |
|------|------|
| 总对话数 | 681条 |
| 总提问数 | 3,996条 |
| 总回答数 | 4,131条 |
| 总思考数 | 4,005条 |
| 总代码块数 | 72,239个 |

### 处理后的文件
- `conversations.json` - 原始对话数据
- `整理后完整内容.txt` - 整理后的完整内容
- `ALL_RESPONSES_COMPACT.txt` - 精简版回答
- `ALL_RESPONSES_COMPLETE.txt` - 完整版回答
- `ALL_RESPONSES_SINGLE_SENTENCE.txt` - 单句版回答


## 六、Coze IDE插件创建步骤

### 1. 创建插件
1. 打开Coze IDE
2. 点击左侧"插件" → "创建插件"
3. 选择"在IDE中创建"
4. 运行时选择Python 3或JavaScript
5. 插件名称：DeepSeek历史对话超级整理插件

### 2. 配置工具定义
在插件详情页，点击"在IDE中创建工具"，然后点击"添加工具"，设置工具名称和介绍。

### 3. 配置输入输出参数
根据工具需求配置输入和输出参数，确保参数定义正确。

### 4. 编写插件代码
将插件代码复制到IDE中，确保代码可正常运行。

### 5. 测试插件
使用测试功能验证各项功能是否正常工作。


## 七、安全特性

- ✅ 输入净化与防注入
- ✅ 参数验证
- ✅ 环境变量保护
- ✅ 审计日志
- ✅ 完整的错误处理机制
- ✅ 注入防护 (Injection Prevention)
- ✅ 限流控制 (Rate Limiting)


## 八、智能路由系统

插件支持自然语言自动识别意图，无需手动指定action：
- 输入"生成工作流" → 自动路由到工作流模块
- 输入"修复JSON" → 自动路由到JSON修复模块
- 输入"训练模型" → 自动路由到AI训练模块
- 输入"处理对话" → 自动路由到DeepSeek处理模块
- 输入"帮我生成一个Python插件" → 自动识别为plugin模块
- 输入"分析电商行业发展趋势" → 自动识别为industry_analysis模块

### 意图关键字映射表

| 关键字 | 目标模块 | 优先级 |
|--------|---------|--------|
| 工作流、workflow、流程、自动化 | workflow | 高 |
| 插件、plugin、工具 | plugin | 高 |
| json、格式、schema | json_fix | 中 |
| 代码、code、bug、错误、修复 | code_fix | 中 |
| 训练、train、模型、微调 | ai_training | 高 |
| 神经、意识、决策、强化学习 | neural_decision | 中 |
| 视频、video、剪辑、图片、image、绘画、音频、声音 | multimedia | 中 |
| 行业、分析、政策、市场 | industry_analysis | 低 |
| 数据、采集、清洗、处理、去重 | data_processing | 中 |
| deepseek、对话 | deepseek | 高 |
| 智能体、agent | smart_agent | 高 |
| 内容、创作 | content_creation | 低 |
| 变现、赚钱 | monetization | 低 |
| 部署、docker、github | devops | 中 |
| openclaw | openclaw | 中 |
| 安全、合规 | security_compliance | 低 |
| 非遗、文化、遗产、洛阳 | luoyang_heritage | 低 |
| 飞书 | feishu | 低 |


## 九、21个核心模块详情

### 1. 统一入口 (universal)
- **工具数**: 1
- **描述**: 智能路由分发，自动识别意图并转发到对应模块

### 2. 工作流自动化 (workflow)
- **工具数**: 21
- **描述**: 工作流生成、修复、执行、调度、监控全流程管理
- **功能**: AI绘画优化、智能修复、工作流创建、工作流执行、工作流监控、工作流调试、工作流优化、工作流备份、工作流导入导出、工作流模板等

### 3. 插件开发 (plugin)
- **工具数**: 15
- **描述**: 插件代码生成、测试、发布、版本管理
- **功能**: 插件自动生成、参数修复、测试、发布、API规范验证、代码审查、依赖分析、安全扫描等

### 4. JSON修复 (json_fix)
- **工具数**: 8
- **描述**: JSON格式修复、Schema验证、格式化、合并
- **功能**: 自动修复、格式化、Schema生成、前缀统一、压缩、比较、合并

### 5. 代码修复 (code_fix)
- **工具数**: 12
- **描述**: 代码错误检测、修复、优化、安全检查
- **功能**: 自动修复、101006错误修复、101008错误修复、类型冲突修复、路径错误修复、测试生成、代码检查、格式化、优化、文档生成、重构、安全检查

### 6. AI训练 (ai_training)
- **工具数**: 14
- **描述**: 模型训练、LoRA微调、数据集处理、GPU调度
- **功能**: 自动训练、LoRA微调、数据喂入、GPU调度、模型优化、数据集准备、超参数调优、模型评估、模型部署、模型注册

### 7. 神经意识决策 (neural_decision)
- **工具数**: 6
- **描述**: 自主决策、自我认知、强化学习、记忆巩固
- **功能**: 自动决策、自我认知、反馈优化、强化学习、动作控制、记忆巩固

### 8. 多媒体制作 (multimedia)
- **描述**: 视频生成、图片处理、音频编辑、风格转换
- **功能**: 视频生成、图片生成、音频处理、字幕生成、视频编辑、图片编辑、语音克隆、背景移除、风格迁移、图片放大、字幕同步、缩略图生成

### 9. 行业分析 (industry_analysis)
- **描述**: 行业分类、政策解读、市场分析、趋势预测
- **功能**: 自动分析、行业分类、政策解读、市场分析、竞品分析、趋势预测、风险评估、机会识别

### 10. 数据处理 (data_processing)
- **描述**: 数据采集、清洗、去重、转换、加密
- **功能**: 自动处理、数据清洗、数据去重、数据转换、数据验证、多源采集、数据聚合、数据过滤、数据连接、数据透视、数据导出、数据采样、数据归一化、数据加密、数据压缩

### 11. 错误修复 (error_fix)
- **工具数**: 10
- **描述**: 运行时错误检测、配置修复、权限修复
- **功能**: 自动修复、错误检测、运行时修复、部署修复、网络修复、配置修复、依赖修复、权限修复、缓存修复、回滚操作

### 12. DeepSeek对话处理 (deepseek)
- **工具数**: 16
- **描述**: 对话解析、代码提取、报告生成、数据合并、历史整理
- **功能**: 解析导出、代码块提取、代码提取、主题分类、对话分类、Markdown报告生成、JSON报告生成、报告生成、对话搜索、统计信息、数据合并、多格式导出、JSON修复、工作流修复、主题提取、工具列表

### 13. 智能体开发 (smart_agent)
- **工具数**: 17
- **描述**: 智能体创建、提示词管理、MCP集成、进化管理
- **功能**: A6AI提示词、单中枢智能体、Coze大模型节点配置、AI模型构建、自动创建Coze LLM节点、MCP创建MCP、插件创建插件、节点自动创建节点、工作流自动创建工作流、自动化生成工作流节点插件、智能体框架架构设计、智能体开发最佳实践、智能体对话管理系统、智能体任务调度系统、智能体知识库管理等

### 14. 内容创作 (content_creation)
- **工具数**: 5
- **描述**: 文案润色、脚本生成、外贸指南、抖音提取
- **功能**: 实时外贸指南、抖音视频信息提取、文本润色、AI脚本生成、高效沟通技巧

### 15. 变现赚钱 (monetization)
- **工具数**: 13
- **描述**: 收入模式、数字员工、工具推荐、质量优化
- **功能**: AI安全自动化收入、赚钱任务模式、非赚钱任务模式、外汇交易风险警告、终极AI数字员工、Claude代码指南、自主AI工具推荐、自主编程工具推荐、AI自动产品创意、喜欢赚钱自我指南、情报洞察、创意生产、质量控制优化

### 16. 部署运维 (devops)
- **描述**: Docker部署、CI/CD集成、环境规划、高可用设计
- **功能**: Docker Hub指南、构建Docker镜像指南、生成安全Docker密码、Docker安装白屏修复、WSL+Docker+Coze配置方案、GitHub Actions功能指南、GitHub Actions集成Coze、Trae终端故障修复、PowerShell执行策略修复、云端自动部署分析、Coze Studio 404修复指南、环境规划、高可用设计

### 17. OpenClaw集成 (openclaw)
- **描述**: OpenClaw配置、免费LLM推荐、MCP工具
- **功能**: OpenClaw完整指南、免费LLM推荐、OmniMCP HyperFactory Ultimate、完美MCP工具V2、合并修复MCP工具内容

### 18. 安全合规 (security_compliance)
- **工具数**: 4
- **描述**: 数据安全、隐私保护、法规合规、内存优化
- **功能**: 安全合规、安全合规网站克隆、本地知识库安全建议、内存溢出修复

### 19. 洛阳非遗 (luoyang_heritage)
- **工具数**: 2
- **描述**: 洛阳文化、方言、职业指南
- **功能**: 洛阳大学生职业指南、洛阳方言开场

### 20. 飞书集成 (feishu)
- **描述**: 飞书助手配置、日程管理、文档助手
- **功能**: 飞书助手搭建

### 21. 通用处理 (general)
- **描述**: NLP处理、翻译、摘要、问答、意图识别
- **功能**: 自动处理、NLP处理、翻译、摘要、问答、意图识别


## 十、企业级特性

- ✅ 智能路由 (Intelligent Routing)
- ✅ 跨工作流执行 (Cross Workflow)
- ✅ 全链路监控 (Full Chain Monitoring)
- ✅ 自动错误恢复 (Auto Error Recovery)
- ✅ 多模态支持 (Multi Modal Support)
- ✅ 权限控制 (Permission Control)
- ✅ 多环境部署 (Multi Environment Deployment)
- ✅ 缓存机制 (Caching)
- ✅ 零Token成本 (Zero Token Cost)


## 十一、144个主题分类（18个类别）

### 1. 单位换算类 (1个)
### 2. 工具设计类 (1个)
### 3. AI训练类 (21个)
### 4. Coze插件类 (33个)
### 5. OpenAPI类 (3个)
### 6. Python开发类 (2个)
### 7. 智能体类 (30个)
### 8. 工作流类 (10个)
### 9. 洛阳非遗类 (2个)
### 10. Docker类 (5个)
### 11. GitHub类 (2个)
### 12. 部署运维类 (7个)
### 13. 内容创作类 (5个)
### 14. 变现赚钱类 (15个)
### 15. 安全合规类 (4个)
### 16. OpenClaw类 (6个)
### 17. 飞书类 (1个)
### 18. 其他工具类 (4个)


## 十二、完整文件清单

### Coze终极插件套件目录保留的完整版本：
- `COZE_ULTIMATE_ALL_IN_ONE_COMPLETE.js` - 完整JavaScript实现
- `COZE_ULTIMATE_ALL_IN_ONE_COMPLETE.json` - 完整配置文件
- `Coze终极插件套件_完整文档.md` - 完整参数文档

### 合并后的文件：
- `合并后_JS完整版.js` - 所有JS文件合并
- `合并后_JSON完整版.json` - 所有JSON文件合并
- `合并后_MD完整版.md` - 所有MD文件合并
- `合并后_TXT完整版.txt` - 所有TXT文件合并


*本文档整合了所有相关md文件的内容，提供了Coze终极插件套件的完整说明。*
