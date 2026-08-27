# Coze 超级插件 — 最终全面验证与摘要计划

## 概述

当前项目已完成全部核心工作（源文件修复、代码转换、合并、handler创建、manifest配置）。本计划仅涵盖最终验证与摘要生成，不涉及任何新的代码修改。

## 当前状态分析

所有工作已在之前的会话中完成：

| 工作项 | 状态 | 详情 |
|--------|------|------|
| 源文件修复（4个） | 已完成 | coze.txt、rgtygfdjshg.txt、yryetrytudkz.txt、ewtreytrudyt.txt |
| Python→JS转换（7个函数） | 已完成 | diagnoseWorkflow、autoFixWorkflow、generateReport、errorClassifier、workflowRepairer、knowledgeRechunk、cardVariableFiller |
| 模板字符串错误修复 | 已完成 | yryetrytudkz.txt 第430行 |
| module.exports→ES6 export | 已完成 | coze.txt第1025行、rgtygfdjshg.txt第385行 |
| Handler文件创建 | 已完成 | 46个handler文件，全部包含export |
| 合并单文件版本 | 已完成 | CozeSuperUltimatePlugin.js（808行，14/14关键组件） |
| manifest.json配置 | 已完成 | 32个模块，46个节点，input_schema/output_schema |
| 源文件复制到source-fixed/ | 已完成 | 4个文件全部就位 |

## 验证步骤

### 步骤 1：source-fixed/ 源文件完整性验证

使用Python脚本验证4个文件：

- `coze.txt`：确认包含 COZE_ULTIMATE_PLUGIN_CONFIG、MODULES_DEFINITION、ROUTING_KEYWORDS、handler函数、ES6 export，无module.exports，无Python代码
- `rgtygfdjshg.txt`：确认7个JS函数全部存在，无Python残留，无module.exports
- `yryetrytudkz.txt`：确认无模板字符串转义错误，无module.exports
- `ewtreytrudyt.txt`：确认4个章节全部存在（核心功能需求、具体功能模块、安全要求、实现方式）

### 步骤 2：merged/CozeSuperUltimatePlugin.js 合并文件验证

确认7个转换函数、AutoFixEngine（9种策略）、handler导出、全部14个关键组件存在。

### 步骤 3：manifest.json 元数据验证

确认JSON语法正确、32个模块、46个节点、input_schema/output_schema存在、安全配置完整。

### 步骤 4：src/handlers/ 处理器文件验证

确认46个handler文件全部存在且包含export语句。

### 步骤 5：运行综合验证脚本

执行Python验证脚本，输出格式化报告，统计通过/失败项。

### 步骤 6：生成完整摘要报告

汇总所有验证结果，输出最终结论。

## 验证依赖关系

```
步骤1 → 步骤2 → 步骤3 → 步骤4
               ↓
         步骤5（综合验证）
               ↓
         步骤6（摘要报告）
```

步骤1-4可并行执行，步骤5依赖前4步，步骤6依赖步骤5。

## 注意事项

- 所有文件使用UTF-8编码读取
- manifest.json中45个节点 vs handler中46个文件：差异源于sql_custom.js为额外节点，标记为INFO
- llm.js和canvas.js同时包含export和module.exports，是兼容性设计，标记为INFO
- 大文件（>1000行）使用tail检查尾部完整性

## 验证结果判定

- 全部通过：输出"所有文件内容完整，无缺失、无遗漏、无代码错误"
- 部分失败：列出失败项，提供修复建议