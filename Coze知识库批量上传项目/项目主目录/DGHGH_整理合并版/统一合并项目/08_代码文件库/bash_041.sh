# 克隆项目
git clone https://github.com/neurofactory/fusion-system.git
cd fusion-system

# 安装依赖
pip install -r requirements.txt

# 创建配置文件
python neurofactory_fusion.py create-config

# 编辑配置文件
vim config/system_config.yaml

# 启动系统
python neurofactory_fusion.py