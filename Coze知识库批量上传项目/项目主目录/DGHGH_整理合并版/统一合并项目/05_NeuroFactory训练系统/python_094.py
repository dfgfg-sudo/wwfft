#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bunny系统配置管理
"""
import torch
import os

class Config:
    """系统配置管理类"""
    
    # 目录配置
    data_dir = "./data"
    checkpoint_dir = "./checkpoints"
    model_dir = "./models"
    log_dir = "./logs"
    
    # 训练配置
    batch_size = 32
    epochs = 100
    learning_rate = 1e-4
    mixed_precision = True
    
    # 设备配置
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 分布式配置
    distributed = False
    world_size = 1
    
    # API配置
    api_host = "0.0.0.0"
    api_port = 8000
    
    # 文件监控配置
    file_monitor_enabled = True
    file_monitor_delay = 1.0
    
    @classmethod
    def init_directories(cls):
        """初始化所有目录"""
        directories = [
            cls.data_dir,
            cls.checkpoint_dir,
            cls.model_dir,
            cls.log_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"目录已创建/确认: {directory}")
    
    @classmethod
    def get_system_info(cls):
        """获取系统配置信息"""
        return {
            "data_dir": cls.data_dir,
            "checkpoint_dir": cls.checkpoint_dir,
            "model_dir": cls.model_dir,
            "log_dir": cls.log_dir,
            "device": cls.device,
            "batch_size": cls.batch_size,
            "epochs": cls.epochs,
            "learning_rate": cls.learning_rate,
            "mixed_precision": cls.mixed_precision,
            "distributed": cls.distributed,
            "api_host": cls.api_host,
            "api_port": cls.api_port
        }