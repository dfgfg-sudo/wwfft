# 1. 克隆项目
git clone https://github.com/autocode-pro/autocode-pro.git
cd autocode-pro

# 2. 安装依赖
npm install
pip install -r requirements.txt

# 3. 设置开发环境
cp .env.development .env

# 4. 启动开发服务
npm run dev

# 5. 运行测试
npm test