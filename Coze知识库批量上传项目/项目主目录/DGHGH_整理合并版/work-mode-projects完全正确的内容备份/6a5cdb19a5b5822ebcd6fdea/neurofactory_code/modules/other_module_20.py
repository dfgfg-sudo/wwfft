#!/bin/bash
set -e
echo "🚀 Coze 插件自动化部署开始"

# 安装依赖
npm install @coze-dev/coze-node-sdk axios node-cache winston

# 语法检查
node -c weather-plugin.js

# 单元测试（若有）
# npm test

# 打包（此处仅为示例，实际可直接上传YAML或代码）
cp weather-plugin.js ./dist/
cp weather.yaml ./dist/

echo "✅ 部署包已准备，请手动上传至 Coze 平台"