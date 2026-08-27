"""
#!/bin/bash
set -e
echo "🚀 Coze 插件自动化部署开始"

npm install @coze-dev/coze-node-sdk axios node-cache winston
node -c weather-plugin.js
cp weather-plugin.js ./dist/
cp weather.yaml ./dist/

echo "✅ 部署包已准备，请手动上传至 Coze 平台"
"""
