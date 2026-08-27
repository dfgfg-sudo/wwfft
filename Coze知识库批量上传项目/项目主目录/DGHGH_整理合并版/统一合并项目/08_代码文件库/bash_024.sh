# 1. 克隆或创建项目
mkdir coze-importer-plugin
cd coze-importer-plugin

# 2. 初始化项目
npm init -y

# 3. 安装依赖
npm install coze-plugin-sdk js-yaml jszip axios

# 4. 安装开发依赖
npm install -D jest eslint @types/node

# 5. 创建项目结构（如前文所示）
mkdir -p src/{nodes,parsers,utils} config assets

# 6. 配置环境变量
echo "COZE_API_KEY=your_api_key_here" > .env
echo "COZE_API_BASE_URL=https://api.coze.cn/v1" >> .env