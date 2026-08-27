#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理模块
"""
import torch
import logging

logger = logging.getLogger("BunnySystem")

class DeviceManager:
    """智能设备管理类"""
    
    def __init__(self):
        self.available_gpus = [f"cuda:{i}" for i in range(torch.cuda.device_count())]
        self.current_device = None
        logger.info(f"检测到可用GPU设备: {self.available_gpus}")
    
    def auto_select(self):
        """自动选择最优设备"""
        if self.available_gpus:
            self.current_device = self.available_gpus[0]
            logger.info(f"自动选择设备: {self.current_device}")
            return self.current_device
        self.current_device = "cpu"
        logger.info("未检测到GPU，使用CPU设备")
        return self.current_device
    
    def get_device_info(self):
        """获取设备详细信息"""
        info = {
            "available_gpus": self.available_gpus,
            "current_device": self.current_device,
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "cuda_device_count": torch.cuda.device_count()
        }
        
        # 添加GPU内存信息
        if torch.cuda.is_available():
            info["gpu_memory"] = self._get_gpu_memory_info()
        
        return info
    
    def _get_gpu_memory_info(self):
        """获取GPU内存信息"""
        memory_info = {}
        for i in range(torch.cuda.device_count()):
            try:
                props = torch.cuda.get_device_properties(i)
                memory_info[f"cuda:{i}"] = {
                    "name": props.name,
                    "total_memory_gb": props.total_memory / (1024**3),
                    "multi_processor_count": props.multi_processor_count
                }
            except Exception as e:
                logger.error(f"获取GPU {i} 信息失败: {str(e)}")
        
        return memory_info