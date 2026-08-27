# Coze 三文件超级合并修复 -- 最终实施计划

## 一、概述

将 `D:\sfdhdjdtysjsy\sgdhfjasdkd\DGHGH\新建文件夹 (2)` 目录下三个源文件（`coze.txt`、`rgtygfdjshg.txt`、`yryetrytudkz.txt`）中的全部 12 个插件和全部工具，合并融合为 **1 个超级插件** 和 **1 个超级工具**，同时修复全部中文文字和代码错误，确保可运行使用。

---

## 二、源文件内容清单

### 文件1: coze.txt (2个插件)
- **knowledge_batch_upload**: Node.js，ZIP批量知识库上传，1个工具
- **DeepSeekAIFactoryUltimate**: Node.js，20模块379工具集成插件

### 文件2: rgtygfdjshg.txt (5个插件)
- **WorkflowAutoFixer**: Python，工作流诊断修复引擎，5个工具
- **Coze终极超级插件**: JavaScript，21模块226工具全能自动化
- **CozeFullStackAutomation**: JavaScript，全链路智能处理，8个工具
- **Plug_in_fully_automated_genera**: JavaScript，插件自动生成器，1个工具
- **CodeIssueDiagnoser**: JavaScript，代码问题诊断器，1个工具

### 文件3: yryetrytudkz.txt (5个插件)
- **coze_plugin_code_generator**: TypeScript，插件代码生成器
- **coze_plugin_generator**: TypeScript，插件自动生成神器
- **Workflow_JSON_Importer**: TypeScript，工作流JSON全能导入器
- **smart_processor**: TypeScript，全功能智能处理插件
- **CozePluginRepairTool**: TypeScript，插件智能修复工具

### 已有项目: coze-super-plugin/
- `manifest.json`: 47个节点定义
- `src/index.ts`: 插件入口（基础框架）
- `src/core/PluginCore.ts`: 节点注册管理（基础框架）
- `src/core/AutoFixEngine.ts`: 自动修复引擎（基础框架）
- `src/handlers/*.js`: 45个节点handler（结构相同，均为class+execute+validateInputs+process+attemptFix+classifyError模式）

---

## 三、需要修复的问题

### 3.1 中文文字问题
- 部分注释和描述需要统一润色
- 错误提示信息需统一格式

### 3.2 代码错误问题
| 问题 | 所在文件 | 修复方案 |
|------|---------|---------|
| Python与JavaScript混合 | rgtygfdjshg.txt | WorkflowAutoFixer的Python函数转换为JavaScript |
| 模板字符串转义错误 `\`` | yryetrytudkz.txt | 替换 `\`` 为正常反引号 |
| handler签名不统一 | 全部文件 | 统一为 `export async function handler({ input, logger })` |
| 缺少export语句 | coze.txt | DeepSeekAIFactoryUltimate用module.exports，需添加ES6 export |
| ROUTING_KEYWORDS重复 | coze.txt + rgtygfdjshg.txt | 合并为单一统一定义 |
| validateParameters重复 | 多文件 | 合并为单一实现 |
| 模块定义不一致 | 多文件 | 统一模块枚举，取并集 |
| TypeScript类型缺失 | yryetrytudkz.txt | 补充完整类型定义 |

---

## 四、合并架构设计

### 4.1 超级插件: CozeSuperUltimatePlugin

**运行时**: Node.js（Coze IDE标准）
**入口**: `export async function handler({ input, logger })`
**版本**: 25.0.0
**总模块数**: 30
**总工具数**: 450+
**总节点数**: 47（沿用已有manifest.json）

### 4.2 统一模块清单 (30个模块)

| 模块ID | 名称 | 来源 | 工具数 |
|--------|------|------|--------|
| universal | 统一入口 | 全部合并 | 5 |
| workflow | 工作流自动化 | coze.txt + rgtygfdjshg.txt | 35 |
| workflow_fix | 工作流修复引擎 | rgtygfdjshg.txt | 10 |
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

### 4.3 统一输入/输出Schema

**输入Schema** (所有工具统一):
- `action`: string，模块ID，默认"universal"
- `sub_action`: string，子操作，默认"auto_handle"
- `user_input`: string，用户输入内容
- `options`: object，包含language/output_format/confidence_threshold/auto_repair/processing_mode

**输出Schema** (所有工具统一):
- `success`: boolean
- `status`: string，pending/running/success/failed
- `module`: string，模块ID
- `module_name`: string，模块名称
- `result`: object，执行结果
- `performance_metrics`: object，含processing_time_ms/confidence_score/modules_executed
- `errors_fixed`: array
- `metadata`: object，含timestamp/version/request_id/total_modules/total_tools

### 4.4 节点Handler统一规范

所有45个handler统一为以下结构:
```javascript
export async function handler({ input, logger }) {
  // 1. 参数验证
  // 2. 核心处理逻辑
  // 3. 自动修复尝试（失败时）
  // 4. 返回统一格式结果
}
```

---

## 五、分步实施计划

### 步骤1: 重写 index.ts -- 超级插件主入口
- 文件: `coze-super-plugin/src/index.ts`
- 合并三个文件的CONFIG、ROUTING_KEYWORDS、MODULES_DEFINITION、ERROR_CODES
- 合并三个文件的validateParameters、determineRoute、detectIntent、executeModule、handler
- 统一export为ES6模块语法

### 步骤2: 重写 PluginCore.ts -- 统一路由核心
- 文件: `coze-super-plugin/src/core/PluginCore.ts`
- 整合三个文件的路由逻辑
- 保留已有的节点注册管理功能
- 添加30个模块的执行器映射

### 步骤3: 重写 AutoFixEngine.ts -- 自动修复引擎
- 文件: `coze-super-plugin/src/core/AutoFixEngine.ts`
- 将rgtygfdjshg.txt中的Python函数（diagnose_workflow、auto_fix_workflow、error_classifier、workflow_repairer、knowledge_rechunk、card_variable_filler）转换为JavaScript
- 整合yryetrytudkz.txt中的CozePluginRepairEngine类
- 保留已有的修复策略

### 步骤4: 创建30个模块执行器文件
- 目录: `coze-super-plugin/src/modules/`
- 为每个模块创建独立文件（如 `workflow.js`、`plugin.js`、`json_fix.js` 等）
- 合并各源文件中对应的executeModule子函数

### 步骤5: 修复45个节点handler
- 目录: `coze-super-plugin/src/handlers/`
- 将每个handler从 `class + module.exports` 改为 `export async function handler({ input, logger })`
- 确保每个handler有完整的输入/输出参数定义（以注释形式）
- 修复中文注释和错误提示

### 步骤6: 更新 manifest.json
- 文件: `coze-super-plugin/manifest.json`
- 添加30个模块定义
- 更新版本号为25.0.0
- 完善元数据（描述、标签、权限等）

### 步骤7: 生成单文件合并版
- 文件: `coze-super-plugin/merged/CozeSuperUltimatePlugin.js`
- 将所有代码合并为单个文件，可直接粘贴到Coze IDE使用
- 包含全部配置、路由、模块执行器、修复引擎、节点handler

### 步骤8: 生成工具参数文档
- 文件: `coze-super-plugin/docs/tool-config.md`
- 列出全部450+工具的输入/输出参数表格
- 列出47个节点的完整参数定义

### 步骤9: 生成需求文本整理版
- 文件: `coze-super-plugin/docs/requirements-clean.md`
- 将用户混乱的输入文本整理为结构清晰的需求文档

---

## 六、输出文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/index.ts` | 重写 | 超级插件主入口，30模块统一路由 |
| `src/core/PluginCore.ts` | 重写 | 统一路由核心 |
| `src/core/AutoFixEngine.ts` | 重写 | 自动修复引擎（含Python转JS） |
| `src/modules/*.js` | 新建 | 30个模块执行器 |
| `src/handlers/*.js` | 修复 | 45个节点handler统一格式 |
| `manifest.json` | 更新 | 完整元数据 |
| `merged/CozeSuperUltimatePlugin.js` | 新建 | 单文件合并版 |
| `docs/tool-config.md` | 新建 | 工具参数文档 |
| `docs/requirements-clean.md` | 新建 | 需求文本整理版 |

---

## 七、验证步骤

1. 检查所有 `export` 语句正确，无语法错误
2. 检查所有 handler 签名统一为 `export async function handler({ input, logger })`
3. 检查中文文字无乱码，语句通顺
4. 检查模板字符串无转义错误
5. 验证 manifest.json 格式正确
6. 验证单文件版可直接在Node.js环境执行
7. 确认所有源文件功能无遗漏

---

## 八、关键决策

1. **统一运行时为 Node.js**: Coze IDE标准运行时，Python代码转换为JavaScript
2. **保留全部功能不删减**: 三个文件的所有功能都保留，去重但不删功能
3. **智能路由优先**: 用户输入自然语言，自动路由到对应模块
4. **双输出模式**: 模块化项目结构 + 单文件合并版
5. **参数规范统一**: 所有工具使用统一的输入/输出Schema
6. **节点handler统一**: 从class模式改为函数式handler，符合Coze IDE规范
