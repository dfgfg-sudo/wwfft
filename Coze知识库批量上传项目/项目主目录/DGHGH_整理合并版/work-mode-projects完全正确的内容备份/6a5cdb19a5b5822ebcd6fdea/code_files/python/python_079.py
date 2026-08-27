#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌌 Neuro Factory Pro - 量子增强AI全能工厂系统
🚀 全栈式多模态AI训练与开发平台
✅ 版本: v3.14 完整版
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('neuro_factory.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主程序入口"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  🌌 Neuro Factory Pro - 量子增强AI全能工厂系统           ║
    ║  🚀 全栈式多模态AI训练与开发平台 v3.14                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查依赖
    check_dependencies()
    
    # 初始化系统
    system = initialize_system()
    
    # 运行系统
    system.run()

def check_dependencies():
    """检查系统依赖"""
    required_packages = [
        'torch', 'transformers', 'pandas', 'numpy',
        'pillow', 'opencv-python', 'gradio', 'streamlit'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少必要的依赖包: {missing_packages}")
        logger.info("请运行: pip install -r requirements.txt")
        sys.exit(1)

def initialize_system():
    """初始化系统组件"""
    from core.quantum_feeder import QuantumFeeder
    from core.data_processor import DataProcessor
    from core.model_trainer import ModelTrainer
    from core.security import QuantumSecurity
    from gui.main_window import MainWindow
    
    # 创建核心组件
    feeder = QuantumFeeder()
    processor = DataProcessor()
    trainer = ModelTrainer()
    security = QuantumSecurity()
    
    # 创建GUI
    gui = MainWindow(feeder, processor, trainer, security)
    
    return System(feeder, processor, trainer, security, gui)

class System:
    """系统总控制器"""
    
    def __init__(self, feeder, processor, trainer, security, gui):
        self.feeder = feeder
        self.processor = processor
        self.trainer = trainer
        self.security = security
        self.gui = gui
        
        logger.info("系统初始化完成")
    
    def run(self):
        """运行系统"""
        try:
            # 启动GUI
            self.gui.run()
        except KeyboardInterrupt:
            logger.info("系统被用户中断")
        except Exception as e:
            logger.error(f"系统运行错误: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()