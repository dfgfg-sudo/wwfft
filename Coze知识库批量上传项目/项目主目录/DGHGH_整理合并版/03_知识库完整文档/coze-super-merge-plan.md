# Coze 三文件超级合并 -- 实施计划

## 一、概述

**目标**: 将 `coze.txt`、`rgtygfdjshg.txt`、`yryetrytudkz.txt` 三个文件中的全部插件和工具代码，合并融合为一个超级强大功能的完整插件和一个超级强大功能的完整工具，修复全部中文文字、全部代码错误，确保可运行使用。

**源文件位置**: `D:\sfdhdjdtysjsy\sgdhfjasdkd\DGHGH\新建文件夹 (2)\`

---

## 二、源文件内容分析

### 文件1: coze.txt (2个插件)
| 插件名 | 语言 | 工具数 | 功能 |
|--------|------|--------|------|
| knowledge_batch_upload | Node.js | 1 | ZIP批量知识库上传，支持Base64解码、目录结构保留、多格式解析 |
| DeepSeekAIFactoryUltimate | Node.js | 379 | 20模块集成插件，智能路由、工作流、插件开发、JSON修复、AI训练等 |

### 文件2: rgtygfdjshg.txt (5个插件)
| 插件名 | 语言 | 工具数 | 功能 |
|--------|------|--------|------|
| WorkflowAutoFixer | Python | 5 | 工作流诊断、自动修复、错误分类、知识库分段、卡片变量填充 |
| Coze终极超级插件 | JavaScript | 226 | 21模块全能自动化，智能路由覆盖全领域 |
| CozeFullStackAutomation | JavaScript | 8 | 全链路智能处理，设备控制、代码工程、内容生成、行业应用 |
| Plug_in_fully_automated_genera | JavaScript | 1 | 插件自动生成器 |
| CodeIssueDiagnoser | JavaScript | 1 | 代码问题诊断器 |

### 文件3: yryetrytudkz.txt (5个插件)
| 插件名 | 语言 | 工具数 | 功能 |
|--------|------|--------|------|
| coze_plugin_code_generator | TypeScript | 1 | 插件代码生成器 |
| coze_plugin_generator | TypeScript | 1 | 插件自动生成神器 |
| Workflow_JSON_Importer | TypeScript | 1 | 工作流JSON全能导入器 |
| smart_processor | TypeScript | 1 | 全功能智能处理插件 |
| CozePluginRepairTool | TypeScript | 1 | 插件智能修复工具 |

### 已有项目结构 (coze-super-plugin/)
- `manifest.json` - 47个节点定义（大模型、插件、工作流、代码、数据库、知识库、图像、视频、会话等）
- `src/handlers/` - 45个handler文件（llm.js, plugin.js, workflow.js, code.js 等）
- `src/core/` - AutoFixEngine.ts, PluginCore.ts

---

## 三、需要修复的问题

### 中文文字问题
1. 部分中文注释编码异常
2. 错误提示信息不统一
3. 参数描述需要润色统一

### 代码错误问题
| 问题 | 所在文件 | 修复方案 |
|------|---------|---------|
| Python与JavaScript混合 | rgtygfdjshg.txt | 统一为JavaScript（Coze IDE标准运行时） |
| 模板字符串转义错误 `\` | yryetrytudkz.txt | 替换 `\` 为正常反引号语法 |
| handler签名不一致 | 全部文件 | 统一为 `export async function handler({ input, logger })` |
| 缺少export导出 | coze.txt | 添加正确的export语句 |
| ROUTING_KEYWORDS重复定义 | rgtygfdjshg.txt | 合并为统一定义 |
| validateParameters重复定义 | 多文件 | 合并为单一实现 |
| 模块ID不一致 | 多文件 | 统一模块枚举 |

---

## 四、合并策略

### 4.1 超级插件架构 (CozeSuperUltimatePlugin)

**统一入口**: `handler({ input, logger })`
**智能路由**: 关键词匹配 + 模块路由
**运行时**: Node.js (Coze IDE标准)

**合并后的模块清单 (共25个模块)**:

| 模块ID | 模块名称 | 来源 | 工具数 |
|--------|----------|------|--------|
| universal | 统一入口 | 全部合并 | 5 |
| workflow | 工作流自动化 | coze.txt + rgtygfdjshg.txt | 35 |
| workflow_fix | 工作流修复引擎 | rgtygfdjshg.txt (Python转JS) | 10 |
| plugin | 插件开发 | coze.txt + rgtygfdjshg.txt | 30 |
| plugin_generator | 插件生成器 | yryetrytudkz.txt + rgtygfdjshg.txt | 5 |
| json_fix | JSON修复 | coze.txt + rgtygfdjshg.txt | 15 |
| code_fix | 代码修复 | coze.txt + rgtygfdjshg.txt | 25 |
| code_diagnoser | 代码诊断 | rgtygfdjshg.txt | 5 |
| ai_training | AI训练 | coze.txt + rgtygfdjshg.txt | 25 |
| neural_decision | 神经意识决策 | coze.txt + rgtygfdjshg.txt | 12 |
| multimedia | 多媒体制作 | coze.txt + rgtygfdjshg.txt | 20 |
| industry_analysis | 行业分析 | coze.txt + rgtygfdjshg.txt | 15 |
| data_processing | 数据处理 | coze.txt + rgtygfdjshg.txt | 25 |
| deepseek | DeepSeek处理 | coze.txt + rgtygfdjshg.txt | 30 |
| smart_agent | 智能体开发 | coze.txt + rgtygfdjshg.txt | 25 |
| content_creation | 内容创作 | coze.txt + rgtygfdjshg.txt | 15 |
| monetization | 变现赚钱 | coze.txt + rgtygfdjshg.txt | 20 |
| devops | 部署运维 | coze.txt + rgtygfdjshg.txt | 20 |
| openclaw | OpenClaw集成 | coze.txt + rgtygfdjshg.txt | 12 |
| security_compliance | 安全合规 | coze.txt + rgtygfdjshg.txt | 10 |
| knowledge_base | 知识库管理 | coze.txt + rgtygfdjshg.txt | 30 |
| knowledge_upload | 知识库批量上传 | coze.txt | 5 |
| fullstack | 全链路自动化 | rgtygfdjshg.txt | 8 |
| smart_processor | 智能处理 | yryetrytudkz.txt | 5 |
| plugin_repair | 插件修复 | yryetrytudkz.txt | 10 |
| workflow_import | 工作流导入 | yryetrytudkz.txt | 5 |
| report_generator | 报告生成 | coze.txt | 15 |
| luoyang_heritage | 洛阳非遗 | rgtygfdjshg.txt | 5 |
| feishu | 飞书集成 | rgtygfdjshg.txt | 5 |
| unit_conversion | 单位换算 | rgtygfdjshg.txt | 3 |

**合并后总工具数**: 约 450+ 工具

### 4.2 超级工具架构

将所有45个节点handler（来自已有 coze-super-plugin/manifest.json）与上述模块功能整合：

**节点分类**:
- 核心节点 (3): 大模型、插件、工作流
- 业务逻辑 (6): 代码、选择器、意图识别、循环、批处理、变量聚合、异步任务
- 输入输出 (2): 输入、输出
- 数据库 (5): SQL自定义、新增、更新、查询、删除
- 知识库 (5): 写入、检索、删除、变量赋值、长期记忆写入/检索
- 图像 (5): 图像生成、画板、抠图、提示词优化、画质提升
- 视频 (3): 视频生成、提取音频、抽帧
- 组件 (5): 问答、文本处理、HTTP请求、JSON序列化/反序列化
- 会话 (6): 创建/修改/删除/查询会话、查询/清空历史
- 消息 (4): 创建/修改/删除/查询消息

### 4.3 统一元数据规范

```json
{
  "manifest_version": 2,
  "name": "Coze超级终极插件 - 全功能合并版",
  "name_en": "CozeSuperUltimatePlugin",
  "version": "25.0.0",
  "description": "合并coze.txt、rgtygfdjshg.txt、yryetrytudkz.txt三个文件的全部插件和工具，包含30个模块、450+工具、47个节点handler，支持工作流自动化、插件开发、JSON修复、代码修复、AI训练、知识库管理、全链路自动化等全领域需求。完全免费，安全合规。",
  "author": "Universal Automation Team",
  "license": "MIT",
  "runtime": "nodejs",
  "total_modules": 30,
  "total_tools": 450,
  "total_nodes": 47,
  "entry_point": "handler",
  "modules": ["universal", "workflow", "workflow_fix", ...],
  "auto_fix": {
    "enabled": true,
    "fix_strategies": ["orange_exclamation_fix", "missing_param_fix", "connection_error_fix", "timeout_retry", "fallback_handler", "json_repair", "code_repair", "plugin_merge"]
  }
}
```

### 4.4 统一输入/输出参数规范

**统一输入Schema**:
```json
{
  "type": "object",
  "properties": {
    "action": { "type": "string", "description": "模块ID，如workflow/plugin/json_fix等", "default": "universal" },
    "sub_action": { "type": "string", "description": "子操作，如auto_handle/auto_fix/generate等", "default": "auto_handle" },
    "user_input": { "type": "string", "description": "用户输入内容（自然语言或数据）" },
    "options": {
      "type": "object",
      "properties": {
        "language": { "type": "string", "default": "zh-CN" },
        "output_format": { "type": "string", "enum": ["json", "text", "html"], "default": "json" },
        "confidence_threshold": { "type": "number", "default": 0.6 },
        "auto_repair": { "type": "boolean", "default": true },
        "processing_mode": { "type": "string", "enum": ["simple", "standard", "advanced"], "default": "standard" }
      }
    }
  },
  "required": ["user_input"]
}
```

**统一输出Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "status": { "type": "string", "enum": ["pending", "running", "success", "failed"] },
    "module": { "type": "string" },
    "module_name": { "type": "string" },
    "detected_intent": { "type": "string" },
    "action": { "type": "string" },
    "result": { "type": "object" },
    "performance_metrics": {
      "type": "object",
      "properties": {
        "processing_time_ms": { "type": "number" },
        "confidence_score": { "type": "number" },
        "modules_executed": { "type": "array", "items": { "type": "string" } }
      }
    },
    "errors_fixed": { "type": "array" },
    "metadata": {
      "type": "object",
      "properties": {
        "timestamp": { "type": "number" },
        "version": { "type": "string" },
        "request_id": { "type": "string" },
        "total_modules": { "type": "number" },
        "total_tools": { "type": "number" }
      }
    }
  }
}
```

---

## 五、分步实施计划

### 步骤1：创建合并后的超级插件主文件
- 文件: `coze-super-plugin/src/index.ts` (重写)
- 内容: 统一配置、路由关键词、模块定义、错误码表、输入/输出Schema
- 合并来源: coze.txt的CONFIG + rgtygfdjshg.txt的CONFIG

### 步骤2：创建统一路由与入口函数
- 文件: `coze-super-plugin/src/core/PluginCore.ts` (重写)
- 内容: validateParameters, determineRoute, detectIntent, executeModule, handler
- 合并来源: 三个文件的handler和路由逻辑

### 步骤3：创建自动修复引擎
- 文件: `coze-super-plugin/src/core/AutoFixEngine.ts` (重写)
- 内容: 工作流诊断、JSON修复、代码修复、插件合并、知识库分段
- 合并来源: rgtygfdjshg.txt的Python函数转JavaScript + yryetrytudkz.txt的CozePluginRepairEngine

### 步骤4：创建30个模块的执行器
- 为每个模块创建独立文件: `coze-super-plugin/src/modules/{module_id}.js`
- 合并各文件中的executeModule子函数

### 步骤5：更新47个节点handler
- 修复已有 `src/handlers/*.js` 文件
- 确保每个handler有完整的输入/输出参数定义
- 统一handler签名

### 步骤6：更新manifest.json
- 添加全部30个模块定义
- 更新版本号为25.0.0
- 完善元数据

### 步骤7：生成合并后的完整代码文件
- 输出: `coze-super-plugin/merged/CozeSuperUltimatePlugin.js` (单文件版)
- 包含所有功能，可直接粘贴到Coze IDE

### 步骤8：生成工具配置文档
- 输出: `coze-super-plugin/docs/tool-config.md`
- 包含全部450+工具的输入/输出参数表格

### 步骤9：验证
- 检查所有export语句正确
- 检查handler签名统一
- 检查中文文字无乱码
- 检查模板字符串无转义错误
- 验证JSON配置文件格式正确

---

## 六、输出文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `coze-super-plugin/src/index.ts` | 重写 | 超级插件主入口 |
| `coze-super-plugin/src/core/PluginCore.ts` | 重写 | 统一路由核心 |
| `coze-super-plugin/src/core/AutoFixEngine.ts` | 重写 | 自动修复引擎 |
| `coze-super-plugin/src/modules/*.js` | 新建 | 30个模块执行器 |
| `coze-super-plugin/src/handlers/*.js` | 修复 | 47个节点handler |
| `coze-super-plugin/manifest.json` | 更新 | 完整元数据 |
| `coze-super-plugin/merged/CozeSuperUltimatePlugin.js` | 新建 | 单文件合并版 |
| `coze-super-plugin/docs/tool-config.md` | 新建 | 工具参数文档 |

---

## 七、关键决策

1. **统一运行时为Node.js**: Coze IDE对Node.js支持最成熟，Python代码转换为JavaScript
2. **保留全部功能不删减**: 三个文件的所有功能都保留，去重但不删功能
3. **智能路由优先**: 用户输入自然语言，自动路由到对应模块
4. **单文件+模块化双输出**: 既提供可粘贴的单文件版，也保留模块化项目结构
5. **参数规范统一**: 所有工具使用统一的输入/输出Schema框架
