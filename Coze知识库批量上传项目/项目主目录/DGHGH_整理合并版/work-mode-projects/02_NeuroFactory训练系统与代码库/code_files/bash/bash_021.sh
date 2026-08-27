#!/bin/bash
# deploy.sh - 部署脚本

# 1. 安装依赖
pip install -r requirements.txt

# requirements.txt 内容：
# aiohttp>=3.8.0
# jinja2>=3.1.0
# pyyaml>=6.0
# pandas>=2.0.0
# tabulate>=0.9.0

# 2. 创建目录结构
mkdir -p {templates,logs,data,output}

# 3. 设置环境变量
export COZE_API_KEY="your_api_key_here"
export DB_CONNECTION="your_db_connection_string"

# 4. 运行自动化处理
python main_controller.py --mode run

# 5. 查看监控面板
python main_controller.py --mode monitor