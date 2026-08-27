#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperAI Fusion System - Trae-CN兼容完整版
主程序入口
"""

import os
import sys
import torch
import numpy as np
import yaml
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from configs.base_config import BaseConfig
from data.preprocessors import CompleteDataPreprocessor
from models.fusion_models import SuperAIFusionSystem
from training.trainers import CompleteTrainingSystem
from evaluation.evaluators import ModelEvaluator
from deployment.serving import ModelServer
from utils.logger import setup_logger, TraeLogger

class SuperAIFusionApplication:
    """SuperAI Fusion System 完整应用类 - Trae-CN兼容"""
    
    def __init__(self, config_path: str = None, trae_mode: bool = True):
        """
        初始化应用
        
        Args:
            config_path: 配置文件路径
            trae_mode: 是否启用Trae-CN兼容模式
        """
        self.trae_mode = trae_mode
        self.config = self.load_config(config_path)
        self.device = self.setup_device()
        self.logger = self.setup_logging()
        self.components = {}
        
        # 初始化Trae-CN兼容组件
        if trae_mode:
            self.init_trae_components()
        
        self.logger.info("🚀 SuperAI Fusion System 初始化完成")
        self.logger.info(f"📋 配置模式: {'Trae-CN兼容' if trae_mode else '标准'}")
        self.logger.info(f"⚙️  设备: {self.device}")
    
    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """加载配置文件"""
        if config_path is None:
            config_path = project_root / "configs" / SuperAI Fusion System - 完整项目实现 (Trae-AI-IDE / Trae-CN 兼容版)

🏗️ 完整项目结构