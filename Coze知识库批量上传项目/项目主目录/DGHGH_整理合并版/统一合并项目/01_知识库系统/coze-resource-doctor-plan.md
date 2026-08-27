# Coze 资源诊断修复助手 -- 实施计划

## 一、概述

**目标**: 通过 browser-use 安全自动化访问用户已登录的 Coze 平台，完成两大任务：
1. 提取并修复所有工作流/对话流/插件/智能体的运行错误和警告
2. 创建一个 Coze IDE 风格的超级插件（CozeResourceDoctor），包含完整的输入/输出参数和元数据

**核心约束**:
- 所有操作通过 browser-use 在用户已登录的浏览器中安全执行
- 完全免费，符合 Coze 官方规范
- 插件具备完整的元数据、输入/输出参数定义

---

## 二、当前状态分析

- 用户浏览器已打开且已登录 Coze 平台
- 用户在之前对话中上传了图片（图片1-5），描述了具体的错误和需求
- 当前会话无法直接看到之前对话的图片，需要通过 browser-use 截图当前页面来识别问题
- 用户需要：修复橘黄色叹号警告、知识库去重、资源列表完整性修复、创建超级插件

---

## 三、分步实施计划

### 第一阶段：资源扫描与问题提取

#### 步骤1：检查浏览器状态，确认 Coze 登录
- 使用 browser-tabs 检查当前标签页列表
- 如果已有 Coze 标签页则切换，否则导航到 `https://www.coze.cn`
- 截图确认登录状态

#### 步骤2：扫描资源库，提取所有资源信息
- 导航到 Coze 工作空间 -> 资源库
- 分别进入：工作流、对话流、插件、智能体、知识库
- 提取每个资源的：名称、ID、类型、状态、最后编辑时间
- 记录所有带红色错误标记或橘黄色叹号警告的资源

#### 步骤3：逐个进入有问题的资源，详细记录错误
- 对每个带警告/错误标记的资源，点击进入详情页/画布
- 截图错误界面和节点位置
- 记录错误类型：参数缺失、依赖断裂、变量引用错误、API连接异常等
- 特别关注橘黄色叹号的具体原因

#### 步骤4：知识库去重检查
- 导航到知识库管理页面
- 提取所有知识库条目的标题、内容摘要、创建时间
- 基于标题匹配和内容相似度分析，识别重复条目
- 标记待删除的重复项（保留最新版本）

#### 步骤5：资源列表完整性检查
- 检查资源列表中各列（资源名称、类型、编辑时间）是否完整显示
- 如有截断或缺失，记录具体问题

---

### 第二阶段：问题修复

#### 步骤6：修复橘黄色叹号警告
- 进入每个带警告的工作流/对话流画布
- 定位警告节点
- 检查节点的输入/输出参数是否完整填写
- 补全缺失的参数配置
- 保存并验证警告消失

#### 步骤7：修复运行错误
- 进入报错的资源详情页
- 分析错误日志和错误节点
- 根据错误类型执行相应修复：
  - 参数缺失 -> 补全参数值
  - 依赖断裂 -> 重新连接节点
  - 变量引用错误 -> 修正变量名/路径
  - API 连接异常 -> 检查 API 配置
- 保存并重新运行验证

#### 步骤8：知识库去重执行
- 对步骤4中标记的重复条目执行删除
- 每删除一条后确认对话框
- 删除完成后验证知识库无重复

#### 步骤9：验证所有修复
- 重新扫描资源库，确认无错误/警告标记
- 进入之前有问题的资源，确认正常运行

---

### 第三阶段：创建 Coze IDE 超级插件

#### 步骤10：在 Coze IDE 中创建插件框架
- 导航到：工作空间 -> 资源库 -> 插件 -> 创建插件
- 选择"在 Coze IDE 中创建"
- 运行时选择 Python3
- 填写插件名称：`CozeResourceDoctor`
- 填写插件描述

#### 步骤11：定义 5 个工具的完整参数

**工具1: scan_resources（扫描资源问题）**

输入参数:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| workspace_id | string | 是 | 无 | 工作空间ID，从Coze URL获取 |
| resource_type | string | 否 | "all" | 资源类型: all/workflow/bot/plugin/knowledge |
| scan_depth | string | 否 | "surface" | 扫描深度: surface(仅列表)/deep(进入详情) |

输出参数:
| 参数名 | 类型 | 说明 |
|-------|------|------|
| scan_result | object | 扫描结果对象 |
| scan_result.total_resources | integer | 扫描的资源总数 |
| scan_result.error_count | integer | 错误数量 |
| scan_result.warning_count | integer | 警告数量 |
| scan_result.issues | array | 问题列表，每项含: resource_name, resource_type, issue_type, issue_description, node_id, suggested_fix |

**工具2: fix_workflow_error（修复工作流错误）**

输入参数:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| workflow_id | string | 是 | 无 | 工作流ID |
| node_id | string | 是 | 无 | 需修复的节点ID |
| fix_type | string | 否 | "auto" | 修复类型: auto/param_missing/dependency/config/variable_ref |
| fix_params | object | 否 | 无 | 手动指定修复参数(含param_name和param_value) |

输出参数:
| 参数名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 是否成功 |
| message | string | 修复结果描述 |
| changes_made | array | 修改记录，每项含: field, before, after |

**工具3: deduplicate_knowledge（知识库去重）**

输入参数:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| knowledge_base_id | string | 是 | 无 | 知识库ID |
| similarity_threshold | number | 否 | 0.9 | 相似度阈值(0.5-1.0)，越高越严格 |
| strategy | string | 否 | "both" | 去重策略: title_match/content_similar/both |
| keep_newest | boolean | 否 | true | 保留最新条目 |

输出参数:
| 参数名 | 类型 | 说明 |
|-------|------|------|
| total_entries | integer | 知识库总条目数 |
| duplicate_groups | integer | 检测到的重复组数 |
| removed_count | integer | 删除的条目数 |
| remaining_count | integer | 保留的条目数 |
| removed_entries | array | 删除记录，每项含: entry_id, entry_title, duplicate_reason |

**工具4: validate_plugin_config（验证插件配置）**

输入参数:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| plugin_id | string | 是 | 无 | 要验证的插件ID |
| check_items | array | 否 | ["all"] | 检查项: input_params/output_params/auth_config/api_endpoint |

输出参数:
| 参数名 | 类型 | 说明 |
|-------|------|------|
| valid | boolean | 是否有效 |
| plugin_name | string | 插件名称 |
| issues | array | 问题列表，每项含: check_item, issue, severity(critical/warning/info) |

**工具5: repair_agent_flow（修复智能体对话流）**

输入参数:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|--------|------|
| agent_id | string | 是 | 无 | 智能体(Bot)ID |
| flow_id | string | 否 | 自动选择 | 对话流ID |
| repair_scope | string | 否 | "all" | 修复范围: connections/params/all |

输出参数:
| 参数名 | 类型 | 说明 |
|-------|------|------|
| success | boolean | 是否成功 |
| repairs | array | 修复记录，每项含: node_name, repair_action, result(fixed/skipped/failed) |
| summary | string | 修复摘要 |

#### 步骤12：定义插件元数据

```json
{
  "plugin_name": "CozeResourceDoctor",
  "display_name": "Coze 资源诊断修复助手",
  "description": "自动诊断和修复Coze平台工作流、对话流、插件、智能体的运行错误、警告和知识库重复问题。一键扫描、批量修复、安全合规、完全免费。",
  "version": "1.0.0",
  "icon": "tool",
  "category": "efficiency",
  "tags": ["自动化", "诊断", "修复", "工作流", "知识库"],
  "author": "Coze User",
  "runtime": "python3"
}
```

#### 步骤13：编写 Python3 工具代码
- 为每个工具编写 handler 函数
- 通过 Coze API 或模拟 UI 操作实现具体修复逻辑
- 包含完善的日志记录和错误处理

#### 步骤14：调试和发布
- 在 Coze IDE 中逐个调试每个工具
- 修复调试中发现的问题
- 发布插件到工作空间

---

### 第四阶段：验证

#### 步骤15：端到端验证
- 使用创建的插件执行一次完整的资源扫描
- 对发现的问题执行批量修复
- 验证所有修复结果
- 确认知识库无重复内容

---

## 四、关键决策与假设

1. **使用 browser-use 而非直接 API**: Coze 平台部分操作需要 UI 交互，browser-use 可以利用用户已登录的 session
2. **插件运行时选择 Python3**: Coze IDE 对 Python3 支持最成熟，生态最完善
3. **5 个工具覆盖所有需求**: 扫描、修复工作流、知识库去重、验证插件、修复对话流，覆盖用户描述的全部场景
4. **先修复再创建**: 先通过 browser-use 修复现有问题，再将修复逻辑封装为插件，便于后续自动化使用

## 五、风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| 无法看到之前图片 | 无法精确定位问题 | 通过 browser-use 截图当前页面获取实际状态 |
| Coze 反自动化检测 | 可能触发验证码 | 使用 browser_waiting_for_user_interaction 暂停让用户处理 |
| 部分操作无法自动化 | 修复不完整 | 记录未完成项，提供手动修复指引 |
| 插件审批延迟 | 上架慢 | 先发布到个人工作空间即可使用 |
