#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识蒸馏训练器模块
"""
import torch
from torch.cuda.amp import autocast, GradScaler
import torch.nn as nn
import logging

logger = logging.getLogger("BunnySystem")

class DistillationTrainer:
    """知识蒸馏训练器"""
    
    def __init__(self, teacher, student, config):
        self.teacher = teacher.to(config.device)
        self.student = student.to(config.device)
        self.config = config
        
        self.optimizer = torch.optim.Adam(
            student.parameters(), 
            lr=config.learning_rate
        )
        
        self.scaler = GradScaler(enabled=config.mixed_precision)
        self.loss_fn = nn.KLDivLoss()
        
        logger.info("知识蒸馏训练器初始化完成")
    
    def train_step(self, data):
        """单步训练"""
        # 准备数据
        inputs = self._prepare_inputs(data)
        if inputs is None:
            return None
        
        self.optimizer.zero_grad()
        
        with autocast(enabled=self.config.mixed_precision):
            # 教师模型预测
            with torch.no_grad():
                teacher_outputs = self.teacher(inputs)
            
            # 学生模型预测
            student_outputs = self.student(inputs)
            
            # 知识蒸馏损失
            loss = self.loss_fn(student_outputs, teacher_outputs.detach())
        
        # 反向传播
        self.scaler.scale(loss).backward()
        self.scaler.step(self.optimizer)
        self.scaler.update()
        
        return loss.item()
    
    def _prepare_inputs(self, data):
        """准备输入数据"""
        if data is None:
            return None
        
        batch_size = self.config.batch_size
        device = self.config.device
        
        # 根据数据类型生成模拟输入
        if isinstance(data, dict) and 'type' in data:
            if data['type'] in ['text', 'pdf']:
                return torch.randn(batch_size, 784, device=device)
            elif data['type'] == 'image':
                return torch.randn(batch_size, 3, 224, 224, device=device)
        
        # 默认输入
        return torch.randn(batch_size, 784, device=device)
    
    def train(self, dataloader, epochs=None):
        """完整训练流程"""
        epochs = epochs or self.config.epochs
        logger.info(f"开始知识蒸馏训练，共 {epochs} 个epochs")
        
        for epoch in range(epochs):
            self.teacher.eval()
            self.student.train()
            
            total_loss = 0
            batch_count = 0
            
            for batch_idx, batch_data in enumerate(dataloader):
                loss = self.train_step(batch_data)
                if loss is not None:
                    total_loss += loss
                    batch_count += 1
                
                if batch_idx % 10 == 0:
                    logger.info(f"Epoch: {epoch+1}/{epochs}, Batch: {batch_idx}, Loss: {loss if loss else 'N/A'}")
            
            if batch_count > 0:
                avg_loss = total_loss / batch_count
                logger.info(f"Epoch {epoch+1} 完成，平均损失: {avg_loss:.4f}")
            else:
                logger.warning(f"Epoch {epoch+1} 没有有效数据")