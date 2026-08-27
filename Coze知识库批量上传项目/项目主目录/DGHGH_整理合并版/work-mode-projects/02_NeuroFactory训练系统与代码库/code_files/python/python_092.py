#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态数据集模块
"""
from torch.utils.data import Dataset
from pathlib import Path
import logging

logger = logging.getLogger("BunnySystem")

class MultiModalDataset(Dataset):
    """多模态数据集类"""
    
    def __init__(self, data_dir, processor):
        self.data_dir = Path(data_dir)
        self.processor = processor
        self.samples = self._discover_samples()
    
    def _discover_samples(self):
        """发现所有数据样本"""
        samples = []
        extensions = ['*.txt', '*.md', '*.jpg', '*.png', '*.jpeg', '*.pdf', '*.csv', '*.xlsx']
        
        for ext in extensions:
            try:
                files = list(self.data_dir.rglob(ext))
                samples.extend(files)
            except Exception as e:
                logger.error(f"扫描 {ext} 文件时出错: {str(e)}")
        
        logger.info(f"总共发现 {len(samples)} 个数据样本")
        return samples
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        """获取数据样本"""
        filepath = self.samples[idx]
        ext = filepath.suffix.lower()
        
        if ext in ['.txt', '.md']:
            data = self.processor.load_text(filepath)
        elif ext in ['.jpg', '.png', '.jpeg']:
            data = self.processor.load_image(filepath)
        elif ext == '.pdf':
            data = self.processor.load_pdf(filepath)
        elif ext in ['.csv', '.xlsx']:
            data = self.processor.load_table(filepath)
        else:
            data = None
        
        return {
            'filepath': str(filepath),
            'data': data,
            'type': ext[1:]  # 移除点号
        }