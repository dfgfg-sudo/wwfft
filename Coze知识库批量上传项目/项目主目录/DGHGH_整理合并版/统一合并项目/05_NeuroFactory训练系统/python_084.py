#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型定义模块
"""
import torch.nn as nn
import torch
import logging

logger = logging.getLogger("BunnySystem")

class SelfHealingModel(nn.Module):
    """自修复模型基类"""
    
    def __init__(self, input_size=784, hidden_size=512, num_classes=10):
        super().__init__()
        self.safe_mode = False
        self.recovery_attempts = 0
        
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.1)
    
    def forward(self, x):
        """前向传播 with 自修复机制"""
        try:
            if self.safe_mode:
                with torch.no_grad():
                    return self._forward_impl(x)
            return self._forward_impl(x)
        except Exception as e:
            logger.error(f"模型前向传播错误: {str(e)}")
            self.recovery_attempts += 1
            self.safe_mode = True
            return self(x)  # 重试
    
    def _forward_impl(self, x):
        """实际的前向传播实现"""
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class TeacherModel(SelfHealingModel):
    """教师模型 - 复杂网络"""
    
    def __init__(self, input_size=784, hidden_size=1024, num_classes=10):
        super().__init__(input_size, hidden_size, num_classes)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
    
    def _forward_impl(self, x):
        """教师模型前向传播"""
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return torch.softmax(x, dim=1)

class StudentModel(SelfHealingModel):
    """学生模型 - 轻量网络"""
    
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        super().__init__(input_size, hidden_size, num_classes)
    
    def _forward_impl(self, x):
        """学生模型前向传播"""
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)