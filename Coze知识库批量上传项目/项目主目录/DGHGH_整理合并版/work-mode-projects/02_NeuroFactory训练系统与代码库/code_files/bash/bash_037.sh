# 1. 安装依赖
pip install torch transformers datasets pandas numpy watchdog pyyaml cryptography scikit-learn pdfplumber python-docx pillow aiohttp

# 2. 创建目录结构
mkdir -p data models logs config

# 3. 创建配置文件
python omnineuro_fusion.py create-config

# 4. 启动系统
python omnineuro_fusion.py