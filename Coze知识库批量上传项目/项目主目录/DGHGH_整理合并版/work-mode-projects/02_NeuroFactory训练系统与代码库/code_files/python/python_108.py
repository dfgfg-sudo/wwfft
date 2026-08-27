#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式训练模块
"""
import torch.distributed as dist
import os
import logging

logger = logging.getLogger("BunnySystem")

def setup_distributed():
    """分布式训练初始化"""
    try:
        if not dist.is_initialized():
            dist.init_process_group(backend='nccl')
            local_rank = int(os.environ.get('LOCAL_RANK', 0))
            logger.info(f"分布式训练初始化完成，本地排名: {local_rank}")
            return True
        return False
    except Exception as e:
        logger.error(f"分布式训练初始化失败: {str(e)}")
        return False

def cleanup_distributed():
    """清理分布式训练"""
    if dist.is_initialized():
        dist.destroy_process_group()
        logger.info("分布式训练已清理")