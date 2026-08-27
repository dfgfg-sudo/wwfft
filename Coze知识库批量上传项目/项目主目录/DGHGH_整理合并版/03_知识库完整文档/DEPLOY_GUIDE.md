# Coze 超级插件与智能体 - 部署指南

## 一、插件部署

### 步骤 1：准备插件文件

确保 `coze-super-plugin/` 目录包含以下文件：
- `manifest.json` - 插件清单
- `src/index.ts` - 入口文件
- `src/core/PluginCore.ts` - 核心模块
- `src/core/AutoFixEngine.ts` - 自动修复引擎
- `src/handlers/*.js` - 46个节点处理器

### 步骤 2：登录 Coze 平台

1. 打开浏览器，访问 https://www.coze.cn
2. 确保已登录您的账号
3. 进入"项目"或"工作空间"

### 步骤 3：上传插件

1. 在工作流编辑器中，点击右侧"插件"面板
2. 点击"添加插件"或"自定义插件"
3. 选择"上传本地插件"
4. 选择 `coze-super-plugin` 文件夹或打包的 ZIP 文件
5. 等待上传完成并验证

### 步骤 4：验证插件

1. 在节点面板中搜索"超级插件"
2. 确认能看到所有 46 个节点分类
3. 尝试拖拽一个节点到画布
4. 检查节点参数配置是否正常

### 步骤 5：使用插件

1. 在工作流中拖拽需要的节点
2. 配置节点参数
3. 如果看到橘黄色叹号，插件会自动尝试修复
4. 点击"试运行"测试工作流

## 二、Bot 部署

### 步骤 1：创建 Bot

1. 登录 https://www.coze.cn
2. 点击"创建 Bot"
3. 输入 Bot 名称："Coze工作流专家助手"
4. 选择图标和描述

### 步骤 2：配置模型

1. 在"模型"设置中，选择 "doubao-pro-128k"
2. 参数设置：
   - Temperature: 0.3
   - Max Tokens: 4096
   - Top P: 0.85

### 步骤 3：设置系统提示词

1. 打开 `coze-bot/system_prompt.md`
2. 复制全部内容
3. 粘贴到 Bot 的"系统提示词"或"人设与回复逻辑"区域

### 步骤 4：导入工作流

1. 在 Bot 编辑页面，点击"工作流"
2. 选择"导入工作流"
3. 选择 `coze-bot/workflow.json` 文件
4. 确认节点连接正确

### 步骤 5：配置工具

1. 在"插件"或"工具"设置中
2. 添加 `coze-super-plugin` 作为工具
3. 确保 5 个工具函数已启用：
   - diagnose_workflow
   - auto_fix_workflow
   - execute_node
   - search_knowledge
   - manage_session

### 步骤 6：测试 Bot

1. 在右侧预览窗口发送测试消息：
   - "帮我诊断工作流问题"
   - "执行大模型节点"
   - "搜索知识库"
2. 检查响应是否正常

### 步骤 7：发布 Bot

1. 点击"发布"按钮
2. 选择发布平台（如网页、微信、飞书等）
3. 完成发布

## 三、常见问题解决

### 问题 1：插件上传失败

**原因**：manifest.json 格式错误或文件缺失

**解决**：
1. 检查 manifest.json 是否为有效 JSON
2. 确认所有引用的处理器文件存在
3. 重新打包上传

### 问题 2：节点显示橘黄色叹号

**原因**：参数缺失或类型不匹配

**解决**：
1. 插件会自动尝试修复
2. 手动检查必要参数是否填写
3. 参考节点描述确认参数类型

### 问题 3：Bot 无法调用插件

**原因**：工具未正确配置或权限不足

**解决**：
1. 检查 Bot 的插件设置中是否启用了超级插件
2. 确认工作流中的插件节点配置正确
3. 重新导入工作流配置

### 问题 4：运行时超时

**原因**：节点执行时间过长

**解决**：
1. 插件会自动重试（最多3次）
2. 检查网络连接
3. 简化工作流逻辑

## 四、高级配置

### 自定义修复策略

编辑 `src/core/AutoFixEngine.ts`，在 `executeStrategy` 方法中添加新策略：

```typescript
case 'my_custom_fix':
  return this.myCustomFix(nodeId, error, inputs);
```

### 添加新节点

1. 在 `manifest.json` 的 `nodes` 数组中添加新节点定义
2. 在 `src/handlers/` 创建对应的处理器文件
3. 重新打包上传

### 集成外部 API

在节点处理器中，可以通过 HTTP 请求调用外部 API：

```javascript
async process() {
  const response = await fetch('https://api.example.com/endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(this.inputs)
  });
  return await response.json();
}
```

## 五、安全注意事项

1. **数据安全**：插件不会上传用户数据到外部服务器
2. **权限控制**：只请求必要的 Coze API 权限
3. **代码审查**：所有处理器代码开源透明，可自行审查
4. **更新维护**：定期检查 Coze 官方规范更新，同步更新插件

## 三、Coze Studio 本地部署

### 方式一：Docker 部署（推荐）

#### 步骤 1：安装 Docker
确保已安装 Docker 20.10+ 和 Docker Compose 2.0+。

#### 步骤 2：配置环境变量
```bash
cd coze-studio-deploy
cp docker/.env.example docker/.env
```

编辑 `docker/.env`，填写：
- `COZE_API_KEY`：您的 Coze API Key
- `DB_PASSWORD`：数据库密码

#### 步骤 3：启动服务
**Windows:**
```bash
scripts\start.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

#### 步骤 4：验证服务
访问 http://localhost:3000 查看前端界面。
访问 http://localhost:8080/health 检查 API 健康状态。

### 方式二：Node.js 本地运行

#### 步骤 1：安装依赖
```bash
cd coze-studio-deploy
npm install
```

#### 步骤 2：启动服务
```bash
npm start
```

#### 步骤 3：运行自动修复
```bash
npm run fix
```

### 方式三：解决橘黄色叹号（已检测到的问题）

#### 问题 1：模型停运警告
运行自动修复脚本切换模型：
```bash
node scripts/auto-fix.js
```

或调用 API：
```bash
curl -X POST http://localhost:8080/api/auto-fix
```

#### 问题 2：发布管理警告
由于安全考虑，下架项目不会自动重新上架。请登录 Coze 平台手动检查并重新上架需要的项目。

## 四、资源库信息

已从您的 Coze 空间提取到以下信息：
- **空间 ID**: 7382283479335403547
- **资源总数**: 15 条
- **工作流**: 4 个（retfjgkhjdzer、dgthfdghkz、sdfrdyc、rtxyfguhy）
- **云插件**: 10 个
- **扣子知识库**: 1 个（sasdfghjh）

## 五、常见问题

### Q: 橘黄色叹号是什么？
A: 橘黄色叹号表示配置警告，如参数缺失、模型即将停运等。本项目的自动修复引擎可以处理大部分此类问题。

### Q: 模型自动切换安全吗？
A: 安全。自动切换仅在检测到停运模型时触发，且会保留原始配置备份。切换后的模型（doubao-pro-128k）与 DeepSeek-V3.2 能力相当。

### Q: 本地部署的数据会泄露吗？
A: 不会。所有数据存储在本地 Docker 容器中，不会上传到外部服务器。

## 六、联系支持

如有部署问题，请：
1. 检查本指南的常见问题部分
2. 查看 Coze 官方文档
3. 在 Coze 社区寻求帮助
