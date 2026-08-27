# Coze 超级插件与智能体

## 项目概述

本项目基于用户 Coze 资源库（coze.cn）完整封装了全部 46 个工作流节点功能，创建了一个超级强大的 Coze IDE 自定义插件 + 独立 Coze Bot，支持自动诊断和修复常见问题（橘黄色叹号、参数缺失、运行错误等）。

**特点**：
- 完全免费使用
- 安全合规
- 支持官方 API 规范
- 自动修复常见问题

## 项目结构

```
.
├── coze_resources.json              # 从 coze.cn 提取的资源信息
├── coze-super-plugin/               # Coze IDE 自定义插件
│   ├── manifest.json                # 插件清单（46个节点定义）
│   ├── src/
│   │   ├── index.ts                 # 插件入口
│   │   ├── core/
│   │   │   ├── PluginCore.ts        # 节点注册与管理
│   │   │   └── AutoFixEngine.ts     # 自动修复引擎
│   │   └── handlers/                # 46个节点处理器
│   │       ├── llm.js               # 大模型
│   │       ├── plugin.js            # 插件
│   │       ├── workflow.js          # 工作流
│   │       ├── code.js              # 代码
│   │       ├── selector.js          # 选择器
│   │       ├── intent.js            # 意图识别
│   │       ├── loop.js              # 循环
│   │       ├── batch.js             # 批处理
│   │       ├── aggregate.js         # 变量聚合
│   │       ├── async.js             # 异步任务
│   │       ├── input.js             # 输入
│   │       ├── output.js            # 输出
│   │       ├── sql_custom.js        # SQL自定义
│   │       ├── db_insert.js         # 新增数据
│   │       ├── db_update.js         # 更新数据
│   │       ├── db_query.js          # 查询数据
│   │       ├── db_delete.js         # 删除数据
│   │       ├── kb_write.js          # 知识库写入
│   │       ├── kb_search.js         # 知识库检索
│   │       ├── kb_delete.js         # 知识库删除
│   │       ├── var_assign.js        # 变量赋值
│   │       ├── longmem_write.js     # 长期记忆写入
│   │       ├── longmem_search.js    # 长期记忆检索
│   │       ├── image_gen.js         # 图像生成
│   │       ├── canvas.js            # 画板
│   │       ├── cutout.js            # 抠图
│   │       ├── prompt_opt.js        # 提示词优化
│   │       ├── image_enhance.js     # 画质提升
│   │       ├── video_gen.js         # 视频生成
│   │       ├── video_extract_audio.js  # 视频提取音频
│   │       ├── video_frame.js       # 视频抽帧
│   │       ├── qa.js                # 问答
│   │       ├── text_process.js      # 文本处理
│   │       ├── http.js              # HTTP请求
│   │       ├── json_serialize.js    # JSON序列化
│   │       ├── json_deserialize.js  # JSON反序列化
│   │       ├── session_create.js    # 创建会话
│   │       ├── session_update.js    # 修改会话
│   │       ├── session_delete.js    # 删除会话
│   │       ├── session_list.js      # 查询会话列表
│   │       ├── history_query.js     # 查询会话历史
│   │       ├── history_clear.js     # 清空会话历史
│   │       ├── msg_create.js        # 创建消息
│   │       ├── msg_update.js        # 修改消息
│   │       ├── msg_delete.js        # 删除消息
│   │       └── msg_list.js          # 查询消息列表
│   └── docs/
├── coze-bot/                        # 独立 Coze Bot
│   ├── config.json                  # Bot 配置
│   ├── system_prompt.md             # 系统提示词
│   ├── workflow.json                # 工作流定义
│   └── knowledge/                   # 知识库
├── coze-studio-deploy/              # Coze Studio 开源版本地部署
│   ├── docker/
│   │   ├── docker-compose.yml       # Docker 编排
│   │   └── .env.example             # 环境变量模板
│   ├── config/
│   │   └── studio-config.yaml       # Studio 主配置
│   ├── scripts/
│   │   ├── auto-fix.js              # 自动修复脚本
│   │   ├── start.sh                 # Linux/Mac 启动
│   │   └── start.bat                # Windows 启动
│   ├── frontend/
│   │   └── index.html               # 前端界面
│   ├── server.js                    # API 服务
│   └── package.json                 # 依赖配置
├── coze_resources_full.json         # 完整资源库数据（15条资源）
├── README.md                        # 本文件
└── DEPLOY_GUIDE.md                  # 部署指南
```

## 节点分类

### 核心节点（3个）
- 大模型、插件、工作流

### 业务逻辑（7个）
- 代码、选择器、意图识别、循环、批处理、变量聚合、异步任务

### 输入输出（2个）
- 输入、输出

### 数据库（5个）
- SQL自定义、新增数据、更新数据、查询数据、删除数据

### 知识库（6个）
- 知识库写入、知识库检索、知识库删除、变量赋值、长期记忆写入、长期记忆检索

### 图像处理（5个）
- 图像生成、画板、抠图、提示词优化、画质提升

### 音视频（3个）
- 视频生成、视频提取音频、视频抽帧

### 组件（5个）
- 问答、文本处理、HTTP请求、JSON序列化、JSON反序列化

### 会话管理（6个）
- 创建会话、修改会话、删除会话、查询会话列表、查询会话历史、清空会话历史

### 消息（4个）
- 创建消息、修改消息、删除消息、查询消息列表

## 自动修复功能

插件内置 5 种自动修复策略：

1. **橘黄色叹号修复** (`orange_exclamation_fix`) - 自动填充缺失参数
2. **缺失参数修复** (`missing_param_fix`) - 检测并补全必要参数
3. **连接错误修复** (`connection_error_fix`) - 网络恢复后重试
4. **超时重试** (`timeout_retry`) - 超时后自动重试
5. **兜底处理器** (`fallback_handler`) - 返回安全默认值

## 使用方法

### 插件安装

1. 登录 coze.cn
2. 进入工作流编辑器
3. 点击"添加插件"
4. 上传 `coze-super-plugin` 目录或打包文件
5. 在节点面板中即可看到所有节点

### Bot 部署

1. 登录 coze.cn
2. 创建新 Bot
3. 导入 `coze-bot/config.json`
4. 复制 `system_prompt.md` 内容到系统提示词
5. 导入 `workflow.json` 作为工作流
6. 发布 Bot

### Coze Studio 本地部署

**方式一：Docker 一键启动**
```bash
# Windows
scripts\start.bat

# Linux/Mac
./scripts/start.sh
```

**方式二：Node.js 本地运行**
```bash
cd coze-studio-deploy
npm install
npm start
```

**访问地址：**
- 前端界面: http://localhost:3000
- API 服务: http://localhost:8080

**运行自动修复（解决橘黄色叹号）：**
```bash
node scripts/auto-fix.js
```

## 已发现的问题及修复

### 橘黄色叹号 1：空间配置 > 模型管理
- **问题**：DeepSeek-V3.2 即将停运
- **自动修复**：切换至 doubao-pro-128k
- **状态**：已配置自动切换

### 橘黄色叹号 2：空间配置 > 发布管理
- **问题**：7个已发布项目全部下架
- **修复建议**：请手动检查并重新上架需要的项目

## 安全声明

- 所有操作均为只读或安全写入，不会删除用户数据
- 符合 Coze 官方插件开发规范
- 完全免费，无需额外付费
- 严格遵守中国法律法规

## 技术支持

如有问题，请通过 Coze 平台反馈或查看 DEPLOY_GUIDE.md 获取详细部署说明。
