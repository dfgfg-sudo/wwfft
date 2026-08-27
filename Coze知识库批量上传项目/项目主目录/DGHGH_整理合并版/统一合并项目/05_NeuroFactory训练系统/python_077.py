#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统核心模块
"""
import os
import logging
from watchdog.observers import Observer
import uvicorn

from config import Config
from .device_manager import DeviceManager
from .multimodal_processor import MultiModalProcessor
from .file_monitor import FileMonitor
from .api_server import app

logger = logging.getLogger("BunnySystem")

class BunnySystem:
    """Bunny系统主类"""
    
    def __init__(self):
        self.config = Config()
        self.dev_mgr = DeviceManager()
        self.processor = MultiModalProcessor()
        self.file_monitor = Observer()
        
        self._init_components()
        logger.info("Bunny全栈式智能训练系统初始化完成")
    
    def _init_components(self):
        """初始化所有组件"""
        # 初始化目录
        Config.init_directories()
        
        # 设备初始化
        self.config.device = self.dev_mgr.auto_select()
        logger.info(f"系统使用设备: {self.config.device}")
        
        # 文件监控初始化
        if Config.file_monitor_enabled:
            event_handler = FileMonitor(self.processor, self._on_file_processed)
            self.file_monitor.schedule(
                event_handler, 
                Config.data_dir, 
                recursive=True
            )
    
    def _on_file_processed(self, filepath, data):
        """文件处理完成回调"""
        logger.info(f"文件处理回调: {filepath}")
    
    def run(self):
        """运行系统"""
        try:
            logger.info("启动Bunny全栈式智能训练系统...")
            
            # 显示系统信息
            self._show_system_info()
            
            # 启动文件监控
            if Config.file_monitor_enabled:
                self.file_monitor.start()
                logger.info(f"文件监控已启动，监控目录: {Config.data_dir}")
            
            # 启动API服务
            logger.info(f"启动FastAPI服务: {Config.api_host}:{Config.api_port}")
            uvicorn.run(
                app, 
                host=Config.api_host, 
                port=Config.api_port, 
                log_level="info"
            )
            
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在关闭系统...")
            self.shutdown()
        except Exception as e:
            logger.error(f"系统运行错误: {str(e)}")
            self.shutdown()
    
    def _show_system_info(self):
        """显示系统信息"""
        device_info = self.dev_mgr.get_device_info()
        
        logger.info("=" * 50)
        logger.info("Bunny全栈式智能训练系统 v13.0")
        logger.info("=" * 50)
        logger.info(f"设备信息: {device_info['current_device']}")
        logger.info(f"可用GPU: {len(device_info['available_gpus'])}")
        logger.info(f"API地址: http://{Config.api_host}:{Config.api_port}")
        logger.info("=" * 50)
    
    def shutdown(self):
        """优雅关闭系统"""
        logger.info("正在关闭系统...")
        self.file_monitor.stop()
        self.file_monitor.join()
        logger.info("系统已安全关闭")