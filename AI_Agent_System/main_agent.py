import os
import json
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import yaml
import psutil
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 加载配置
config = {}
try:
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logger.warning('配置文件未找到，使用默认配置')
    config = {
        'port': 5000,
        'host': '0.0.0.0',
        'api_key': 'default_api_key',
        'max_content_length': 10485760,  # 10MB
        'security': {
            'sensitive_words': [],
            'url_blacklist': [],
            'max_content_length': 10485760
        }
    }

# 系统状态监控
def get_system_status():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()