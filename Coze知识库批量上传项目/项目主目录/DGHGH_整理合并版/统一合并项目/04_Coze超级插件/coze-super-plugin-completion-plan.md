# Coze 超级插件合并完成计划

## 概述

将三个源文件（coze.txt、rgtygfdjshg.txt、yryetrytudkz.txt）的全部插件和工具合并融合为一个超级插件和一个超级工具，修复所有中文文本和代码错误，确保内容完整、可运行。

## 当前状态分析

### 已完成工作
- 核心入口文件 `src/index.ts` — 合并了CONFIG、ROUTING_KEYWORDS、MODULES_DEFINITION、ERROR_CODE_TABLE
- 核心路由 `src/core/PluginCore.ts` — 实现30个模块统一路由
- 自动修复引擎 `src/core/AutoFixEngine.ts` — 集成Python转换逻辑和CozePluginRepairEngine
- 清单文件 `manifest.json` — 包含30个模块定义和47个节点
- 单文件版本 `merged/CozeSuperUltimatePlugin.js` — 可直接在Coze IDE使用
- 模块索引 `src/modules/index.ts` — 统一模块注册和查询
- 文档 `docs/tool-config.md` 和 `docs/requirements-clean.md`
- 31个处理器文件已创建

### 待完成工作

| 任务 | 详情 | 优先级 |
|------|------|--------|
| 缺失14个处理器文件 | db_delete, db_update, history_clear, history_query, http, msg_create, msg_delete, msg_list, msg_update, session_create, session_delete, session_list, session_update, sql_custom | 高 |
| 修复yryetrytudkz.txt模板字符串错误 | 第430行和452行：`\\`` 应为 `` ` ``，`\\${` 应为 `${` | 高 |
| 修复rgtygfdjshg.txt Python代码 | 7个Python函数需转为JS（已在PluginCore.ts中完成转换，源文件需同步更新） | 高 |
| 修复coze.txt module.exports | 第1025行 `module.exports` 需改为 ES6 `export` | 高 |
| 复制修复后的源文件到输出目录 | 将三个修复后的源文件复制到工作目录 | 中 |
| 验证单文件版本完整性 | 确保CozeSuperUltimatePlugin.js包含所有功能 | 中 |
| 创建修复后的源文件副本 | 在输出目录保存修复后的coze.txt、rgtygfdjshg.txt、yryetrytudkz.txt | 中 |

## 实施方案

### 步骤1：创建14个缺失处理器文件

在 `coze-super-plugin/src/handlers/` 目录下创建以下文件，参照源目录中对应文件的代码模式，统一为ES6 export格式：

1. **db_delete.js** — 数据库删除处理器（输入：table, condition）
2. **db_update.js** — 数据库更新处理器（输入：table, data, condition）
3. **history_clear.js** — 历史清除处理器（输入：sessionId）
4. **history_query.js** — 历史查询处理器（输入：sessionId, startTime, endTime）
5. **http.js** — HTTP请求处理器（输入：url, method, headers, body）
6. **msg_create.js** — 消息创建处理器（输入：sessionId, content）
7. **msg_delete.js** — 消息删除处理器（输入：msgId）
8. **msg_list.js** — 消息列表处理器（输入：sessionId, limit）
9. **msg_update.js** — 消息更新处理器（输入：msgId, content）
10. **session_create.js** — 会话创建处理器（输入：botId, userId）
11. **session_delete.js** — 会话删除处理器（输入：sessionId）
12. **session_list.js** — 会话列表处理器（输入：botId, limit）
13. **session_update.js** — 会话更新处理器（输入：sessionId, config）
14. **sql_custom.js** — 自定义SQL处理器（输入：sql, params）

每个文件统一代码模式：
- 类定义 + `export async function handler({ input, logger })` 入口
- 参数验证、错误处理、自动修复尝试、错误分类
- `module.exports` 兼容性导出

### 步骤2：修复yryetrytudkz.txt模板字符串错误

**问题位置：**
- 第430行：`suggestion: \\\`支持值：\\\${[${param.enum.map(v => \`"${v}"\`).join(', ')}].join(', ')}\\\``
- 第452行：`suggestion: \\\`\\\${features.errorTypes.find(e => e.code === 'ACTION_FAILED')?.defaultSuggestion || '请稍后重试'}\\\``

**修复方案：**
- 将 `\\\`` 替换为普通反引号 `` ` ``
- 将 `\\\${` 替换为 `${`
- 确保模板字符串语法正确

### 步骤3：修复rgtygfdjshg.txt Python代码

**需转换的7个Python函数：**
1. `diagnose_workflow(config)` → `diagnoseWorkflow(config)` — 已在PluginCore.ts中完成
2. `auto_fix_workflow(config)` → `autoFixWorkflow(config)` — 已在PluginCore.ts中完成
3. `generate_report(...)` → `generateReport(...)` — 已在PluginCore.ts中完成
4. `error_classifier(inp)` → `errorClassifier(inp)` — 已在PluginCore.ts中完成
5. `workflow_repairer(inp)` → `workflowRepairer(inp)` — 已在PluginCore.ts中完成
6. `knowledge_rechunk(inp)` → `knowledgeRechunk(inp)` — 已在PluginCore.ts中完成
7. `card_variable_filler(inp)` → `cardVariableFiller(inp)` — 已在PluginCore.ts中完成

**源文件处理：** 在源文件中将Python代码段替换为等效的JavaScript代码，保留原始注释结构。

### 步骤4：修复coze.txt module.exports

**问题位置：** 第1025行 `module.exports = {`

**修复方案：** 将 `module.exports = { ... }` 替换为 ES6 `export` 语句，保持导出内容不变。

### 步骤5：复制修复后的源文件到输出目录

将三个修复后的源文件复制到：
- `coze-super-plugin/source-fixed/coze.txt`
- `coze-super-plugin/source-fixed/rgtygfdjshg.txt`
- `coze-super-plugin/source-fixed/yryetrytudkz.txt`

### 步骤6：验证单文件版本完整性

检查 `merged/CozeSuperUltimatePlugin.js` 确保包含：
- 全部30个模块的执行器
- 全部9种修复策略
- 全部15个错误码定义
- 统一的handler入口函数
- 安全配置声明

### 步骤7：最终验证

验证清单：
- [ ] 45个处理器文件全部存在且格式统一
- [ ] 三个源文件的代码错误已修复
- [ ] Python代码已转换为JavaScript
- [ ] 模板字符串错误已修复
- [ ] module.exports已改为ES6 export
- [ ] 单文件版本功能完整
- [ ] manifest.json元数据完整
- [ ] 文档完整无缺失

## 假设与决策

1. **源文件修复策略**：在源文件中直接修复代码错误，同时在输出目录保留修复后的副本
2. **处理器文件来源**：参照源目录 `D:\sfdhdjdtysjsy\sgdhfjasdkd\DGHGH\新建文件夹 (2)\coze-super-plugin\src\handlers\` 中已有的45个处理器文件，将缺失的14个复制到输出目录并统一格式
3. **Python转JS**：转换逻辑已在PluginCore.ts中完成，源文件中的Python代码替换为等效JS
4. **单文件版本**：已创建的CozeSuperUltimatePlugin.js作为最终交付物
5. **安全合规**：所有代码本地运行，零Token成本，完全免费

## 输出文件清单

```
coze-super-plugin/
├── src/
│   ├── core/
│   │   ├── PluginCore.ts          ✅ 已完成
│   │   └── AutoFixEngine.ts       ✅ 已完成
│   ├── handlers/                   45个文件（31已完成 + 14待创建）
│   ├── modules/
│   │   └── index.ts               ✅ 已完成
│   └── index.ts                   ✅ 已完成
├── merged/
│   └── CozeSuperUltimatePlugin.js ✅ 已完成
├── docs/
│   ├── tool-config.md             ✅ 已完成
│   └── requirements-clean.md      ✅ 已完成
├── source-fixed/                  待创建
│   ├── coze.txt                   待修复
│   ├── rgtygfdjshg.txt            待修复
│   └── yryetrytudkz.txt           待修复
└── manifest.json                  ✅ 已完成
```
