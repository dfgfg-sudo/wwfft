# 安装CLI工具
npm install -g @autocode-pro/cli

# 初始化配置
autocode init

# 生成项目
autocode generate \
  --description "我需要一个电商平台，包含用户管理、商品展示、购物车、订单系统和支付功能" \
  --name "我的电商平台" \
  --output ./my-ecommerce-project

# 部署项目
autocode deploy ./my-ecommerce-project \
  --platform docker \
  --env production