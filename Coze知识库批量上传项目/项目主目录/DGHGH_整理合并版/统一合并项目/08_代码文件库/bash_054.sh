# 安装依赖
./scripts/setup-server.sh

# 配置环境
cp .env.production .env
vim .env

# 启动服务
./scripts/start-production.sh

# 设置开机自启
sudo systemctl enable autocodepro-api
sudo systemctl enable autocodepro-web