# Coze 终极解决方案实施计划

## 概述

基于用户已确认的 Coze 资源库统计（76个工作流 + 8个对话流 + 25个云插件 + 9个知识库 + 3个提示词 = 121个资源），创建一份完整的终极解决方案，包括：

1. **完整资源提取**：使用 browser-use 安全访问 coze.cn，将当前 42 条扩展到 121 条
2. **超级合并**：将 121 个资源合并为 5 个超级文件（已存在于 `超级合并代码/` 目录，需更新为完整版）
3. **空间配置橘黄色叹号修复**：处理"空间配置"的模型停运警告 + 7个已下架项目警告
4. **模型自动切换器**：将所有停运/付费模型自动切换至完全免费的安全模型
5. **Coze Studio 开源版本地部署**：确保 `coze-studio-deploy` 配置正确

---

## 当前状态分析

### 已完成部分
- ✅ `coze-super-plugin/` 包含 46 个节点处理器和 manifest.json
- ✅ `coze-super-plugin/src/core/ModelAutoSwitcher.ts` 模型自动切换器已创建
- ✅ `coze-super-plugin/src/core/SpaceConfigFixer.ts` 空间配置修复器已创建
- ✅ `coze-super-plugin/src/core/AutoFixEngine.ts` 自动修复引擎已创建
- ✅ `coze_resources_full.json` 包含 42 条资源（需扩展到 121 条）
- ✅ `coze-studio-deploy/` 包含完整本地部署配置
- ✅ `超级合并代码/` 已包含 5 个超级文件骨架（super_cloud_plugin.js, super_dialog_flow.js, super_knowledge_base.js, super_prompt.js, super_workflow.js）

### 待处理问题
- ⚠️ 资源数量：42 → 需要 121
- ⚠️ 空间配置橘黄色叹号未实际修复
- ⚠️ 模型自动切换器仅是代码框架，未集成到 Coze Studio 部署配置
- ⚠️ 超级合并文件需要基于完整 121 条资源重新生成

---

## 实施计划

### 步骤 1：使用 browser-use 完整提取 121 个资源

**目标**：将 `coze_resources_full.json` 从 42 条扩展到 121 条

**操作**：
1. 使用 browser-use 访问 `https://www.coze.cn/space/7382283479335403547/library`
2. 在"工作流"分类下通过点击页面底部分页/滚动加载全部 76 个工作流
3. 在"插件"分类下提取全部 25 个云插件
4. 查找并提取"对话流"分类（如有独立 tab）的 8 个对话流
5. 在"知识库"分类下确认全部 9 个知识库
6. 在"提示词"分类下确认全部 3 个提示词
7. 将完整数据写回 `coze_resources_full.json`

**输出文件**：
- `coze_resources_full.json`（更新版，121 条资源）

### 步骤 2：重新生成 5 个超级合并文件

**目标**：基于完整 121 条资源，重新生成或完善 `超级合并代码/` 中的 5 个超级文件

**操作**：
1. **超级工作流 `super_workflow.js`** - 合并 76 个工作流为统一超级工作流
   - 8 大模块：视频处理、文本处理、代码生成、工作流自动化、思维导图、新闻搜索、网页内容、小红书内容
   - 统一输入输出接口、模块路由器、统一错误处理
2. **超级对话流 `super_dialog_flow.js`** - 合并 8 个对话流
3. **超级云插件 `super_cloud_plugin.js`** - 合并 25 个云插件
4. **超级知识库 `super_knowledge_base.js`** - 合并 9 个知识库（已实现，需更新数据源）
5. **超级提示词 `super_prompt.js`** - 合并 3 个提示词
6. 更新 `index/index.json` 为完整索引

**输出文件**：
- `超级合并代码/super_workflow.js`（含 76 工作流映射）
- `超级合并代码/super_dialog_flow.js`（含 8 对话流映射）
- `超级合并代码/super_cloud_plugin.js`（含 25 插件映射）
- `超级合并代码/super_knowledge_base.js`（含 9 知识库数据）
- `超级合并代码/super_prompt.js`（含 3 提示词）
- `超级合并代码/index/index.json`（完整索引）

### 步骤 3：修复空间配置橘黄色叹号

**目标**：消除"空间配置"菜单的橘黄色叹号

**操作**：
1. **模型停运警告修复**
   - 调用 `SpaceConfigFixer.fixModelDeprecationWarning()`
   - DeepSeek-V3.2 即将停运 → 自动切换至 doubao-pro-128k
   - 添加更多停运模型到映射表
2. **发布管理警告处理**
   - 调用 `SpaceConfigFixer.fixPublishingWarnings()`
   - 7 个已下架项目 → 生成报告供用户确认手动重新上架
3. **空间配置补全**
   - 调用 `SpaceConfigFixer.fixIncompleteConfig()`
   - 补全缺失的描述、时区等

**输出文件**：
- `coze-super-plugin/src/core/SpaceConfigFixer.ts`（增强版，含完整修复报告）

### 步骤 4：完善模型自动切换器

**目标**：将 `ModelAutoSwitcher` 集成到 Coze Studio 部署配置

**操作**：
1. 更新 `coze-studio-deploy/config/studio-config.yaml`，添加完整模型映射：
   ```yaml
   models:
     deprecated:
       - id: "DeepSeek-V3.2"
         replacement: "doubao-pro-128k"
         auto_switch: true
       - id: "DeepSeek-V3"
         replacement: "doubao-pro-128k"
         auto_switch: true
       - id: "DeepSeek-V2.5"
         replacement: "doubao-lite-128k"
         auto_switch: true
       - id: "GPT-4-Turbo"
         replacement: "doubao-pro-128k"
         auto_switch: true
       # ... 完整列表
   ```
2. 创建 `coze-studio-deploy/scripts/auto-switch-models.js`，实现实际的模型切换逻辑
3. 在 `package.json` 中添加 `npm run switch-models` 脚本

**输出文件**：
- `coze-studio-deploy/config/studio-config.yaml`（更新版，含完整模型映射）
- `coze-studio-deploy/scripts/auto-switch-models.js`（新增，自动切换脚本）

### 步骤 5：Coze Studio 本地部署验证

**目标**：确保 Coze Studio 开源版本地部署可用

**操作**：
1. 检查 `docker-compose.yml` 配置完整性
2. 验证 `.env.example` 环境变量
3. 更新 `start.bat` / `start.sh` 启动脚本
4. 添加 `npm run switch-models` 到启动流程

**输出文件**：
- `coze-studio-deploy/docker/docker-compose.yml`（验证/更新）
- `coze-studio-deploy/scripts/start.bat`（更新）
- `coze-studio-deploy/scripts/start.sh`（更新）

### 步骤 6：生成最终完整报告

**目标**：更新 `COMPLETE_REPORT.md`，反映 121 条资源 + 所有修复

**操作**：
1. 更新报告中的资源统计
2. 列出所有超级合并文件
3. 列出所有自动修复的橘黄色叹号
4. 列出所有自动切换的模型
5. 提供部署和使用的完整指南

**输出文件**：
- `COMPLETE_REPORT.md`（最终版）

---

## 关键文件路径

| 文件 | 作用 |
|------|------|
| `coze_resources_full.json` | 资源库完整数据（121 条） |
| `超级合并代码/super_*.js` | 5 个超级合并文件 |
| `coze-super-plugin/src/core/ModelAutoSwitcher.ts` | 模型自动切换器 |
| `coze-super-plugin/src/core/SpaceConfigFixer.ts` | 空间配置修复器 |
| `coze-studio-deploy/config/studio-config.yaml` | Studio 主配置 |
| `coze-studio-deploy/scripts/auto-switch-models.js` | 模型切换脚本 |
| `COMPLETE_REPORT.md` | 最终完整报告 |

---

## 假设与决策

1. **资源数量**：用户已明确提供 121 个资源的分类（76+8+25+9+3），按此目标提取
2. **超级合并策略**：保留 5 个独立超级文件（按用户原始需求结构），每个文件合并对应分类的全部资源
3. **模型自动切换**：使用 `doubao-pro-128k`、`doubao-lite-128k`、`DeepSeek-R1`、`qwen-turbo` 等官方免费模型作为替换目标
4. **橘黄色叹号修复**：仅修复"空间配置"的叹号，发布管理问题生成报告供用户确认
5. **Coze Studio 部署**：使用 Docker 一键启动 + Node.js 本地运行两种方式

---

## 验证步骤

1. ✅ `coze_resources_full.json` 中 `summary.total_resources` = 121
2. ✅ 5 个超级合并文件能正常加载，无语法错误
3. ✅ `SpaceConfigFixer` 能成功修复模型停运警告
4. ✅ `ModelAutoSwitcher` 能识别并列出所有停运模型
5. ✅ `studio-config.yaml` 配置正确，可被 Docker Compose 加载
6. ✅ `COMPLETE_REPORT.md` 反映所有最新数据

---

## 安全与合规

- 所有操作仅基于用户已登录的 coze.cn 浏览器会话
- 资源提取为只读操作，不修改用户数据
- 模型切换脚本使用 `dry-run` 模式预览，需用户确认后执行
- 完全免费模型，零 Token 成本
- 符合 Coze 官方插件开发规范（manifest v2）
