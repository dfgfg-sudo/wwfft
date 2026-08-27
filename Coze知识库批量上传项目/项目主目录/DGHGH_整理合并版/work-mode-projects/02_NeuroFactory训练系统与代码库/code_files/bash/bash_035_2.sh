# 1. 下载完整包
git clone https://github.com/enterprise-workflow/ewio-plugin.git
cd ewio-plugin

# 2. 授予执行权限
chmod +x deploy.sh test.sh

# 3. 一键部署
./deploy.sh

# 4. 自动化测试
./test.sh

# 5. 访问系统
# 监控面板: http://localhost:3000
# API文档: http://localhost/v1/openapi.yaml
# 健康检查: http://localhost/v1/health