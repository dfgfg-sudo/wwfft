# Coze终极插件套件 - 完整文档

## 目录概览

本文档整合了所有相关的md文件内容，包含Coze终极插件套件的完整功能说明、使用指南、参数配置等信息。

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

### 2. 输出参数 (output_schema)

#### 一级参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `success` | Boolean | 是 | 请求是否成功 |
| `status` | String | 是 | 执行状态 |
| `module` | String | 是 | 处理的模块名称 |
| `module_name` | String | 否 | 模块显示名称 |
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
| general | 通用处理 | 通用工具处理 |


## 三、工具列表 (226个工具)

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

### 代码工具
| code_repair | 代码修复 | /tools/code-repair | POST |
| json_format | JSON格式化 | /tools/json-format | POST |
| yaml_to_json | YAML转JSON | /tools/yaml-to-json | POST |
| json_to_yaml | JSON转YAML | /tools/json-to-yaml | POST |

### AI训练工具
| ai_training | AI训练 | /ai/training | POST |
| ai_model_trainer | 模型训练器 | /ai/model-trainer | POST |
| ai_enhancement | AI增强 | /ai/enhancement | POST |

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


## 五、文件功能内容总结

### 整理后完整内容.txt包含的功能：
- **单位换算工具**：公斤与斤换算、价格计算
- **豆包对话框内容提取工具**：可视化界面、导出功能、CPM自动化工具开发平台
- **OpenAPI规范整合与验证工具**：参数验证修复、URL前缀统一、Coze规范兼容
- **本地AI模型训练与数据处理方案**：多格式数据处理、智能编码检测、文本清洗、表格转换、大文件分块、模型训练、模型推理、数据加密、可视化监控、分布式训练
- **AI编程工具与未来开发趋势**：AI程序员工具介绍、实战案例、开发流程、问题解决
- **Coze插件完整配置与修复方案**：GitHub自动化、神经意识决策、内容创作、洛阳非遗电商、工作流自动化


## 六、DeepSeek历史对话整理

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


## 七、Coze IDE插件创建步骤

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


## 八、安全特性

- ✅ 输入净化与防注入
- ✅ 参数验证
- ✅ 环境变量保护
- ✅ 审计日志
- ✅ 完整的错误处理机制


## 九、智能路由系统

插件支持自然语言自动识别意图，无需手动指定action：
- 输入"生成工作流" → 自动路由到工作流模块
- 输入"修复JSON" → 自动路由到JSON修复模块
- 输入"训练模型" → 自动路由到AI训练模块
- 输入"处理对话" → 自动路由到DeepSeek处理模块


## 十、文件清单

### Coze终极插件套件目录保留的完整版本：
- `COZE_ULTIMATE_ALL_IN_ONE_COMPLETE.js` - 完整JavaScript实现
- `COZE_ULTIMATE_ALL_IN_ONE_COMPLETE.json` - 完整配置文件
- `Coze终极全能超级插件_完整参数展开表.md` - 完整参数文档


*本文档整合了所有相关md文件的内容，提供了Coze终极插件套件的完整说明。*