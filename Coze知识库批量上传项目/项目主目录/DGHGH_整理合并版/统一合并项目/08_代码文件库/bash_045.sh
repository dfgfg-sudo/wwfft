# 1. 克隆或创建项目
git clone https://github.com/coze-automation/ultimate-system.git
cd ultimate-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp config.example.json config.json
# 编辑 config.json 文件，设置你的配置

# 4. 设置权限
chmod +x scripts/*.sh