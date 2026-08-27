# 1. 创建智能体
# 在 Coze 平台创建新智能体，命名为 "Coze-Workflow-Generator"

# 2. 配置系统指令
# 将第三部分 "Coze 平台部署版" 的完整内容复制到系统提示词区域

# 3. 开启功能
# - 开启 "代码解释器" 功能

# 4. 使用示例
@Coze-Workflow-Generator 我需要一个每日数据备份流程：
1) 从数据库导出数据
2) 压缩为 zip
3) 上传到 S3
4) 发送钉钉通知

# 5. 获得输出
# - workflow.json（可直接导入）
# - functions.js（可复制到节点）
# - DEPLOY.md（部署说明）