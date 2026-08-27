# -*- coding: utf-8 -*-
"""
多模态融合引擎
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Union

class HyperFusionEngine(nn.Module):
    """超融合引擎"""
    
    def __init__(self, hidden_size: int = 2048, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.hidden_size = hidden_size
        
        # 模态投影层
        self.text_projection = nn.Linear(768, hidden_size)
        self.image_projection = nn.Linear(2048, hidden_size)
        self.audio_projection = nn.Linear(1024, hidden_size)
        
        # 跨模态注意力
        self.cross_attention = nn.MultiheadAttention(
            hidden_size, 
            num_heads, 
            dropout=dropout,
            batch_first=True
        )
        
        # 层归一化
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        
        # 前馈网络
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 4, hidden_size)
        )
        
        # 融合门控
        self.fusion_gate = nn.Sequential(
            nn.Linear(hidden_size * 3, hidden_size),
            nn.Sigmoid()
        )
        
    def forward(self, inputs: Dict[str, torch.Tensor], 
                quantum_features: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        前向传播
        
        Args:
            inputs: 多模态输入字典
            quantum_features: 量子特征（可选）
            
        Returns:
            融合后的特征
        """
        # 投影各模态特征
        projected_features = []
        
        if 'text' in inputs:
            text_features = self.text_projection(inputs['text'])
            projected_features.append(text_features)
            
        if 'image' in inputs:
            image_features = self.image_projection(inputs['image'])
            projected_features.append(image_features)
            
        if 'audio' in inputs:
            audio_features = self.audio_projection(inputs['audio'])
            projected_features.append(audio_features)
            
        # 拼接特征
        if len(projected_features) == 0:
            raise ValueError("至少需要一个模态的输入")
            
        concatenated = torch.cat(projected_features, dim=1)  # [batch, n_modalities * hidden]
        
        # 应用融合门控
        fusion_weights = self.fusion_gate(concatenated)
        
        # 加权融合
        weighted_sum = torch.zeros_like(projected_features[0])
        for i, feat in enumerate(projected_features):
            weight_slice = fusion_weights[:, i*self.hidden_size:(i+1)*self.hidden_size]
            weighted_sum += feat * weight_slice
            
        # 添加量子特征
        if quantum_features is not None:
            weighted_sum = weighted_sum + quantum_features
            
        # 跨模态注意力
        attn_output, _ = self.cross_attention(
            weighted_sum, weighted_sum, weighted_sum
        )
        
        # 残差连接和层归一化
        x = self.norm1(weighted_sum + attn_output)
        
        # 前馈网络
        ff_output = self.feed_forward(x)
        output = self.norm2(x + ff_output)
        
        return output
        
    def fuse_with_attention(self, modality_features: List[torch.Tensor]) -> torch.Tensor:
        """使用注意力机制融合多模态特征"""
        batch_size = modality_features[0].shape[0]
        
        # 创建注意力查询、键、值
        queries = []
        keys = []
        values = []
        
        for feat in modality_features:
            q = self._create_query(feat)
            k = self._create_key(feat)
            v = self._create_value(feat)
            
            queries.append(q)
            keys.append(k)
            values.append(v)
            
        # 拼接所有模态
        all_queries = torch.cat(queries, dim=1)  # [batch, n_modalities, hidden]
        all_keys = torch.cat(keys, dim=1)
        all_values = torch.cat(values, dim=1)
        
        # 计算注意力分数
        attention_scores = torch.matmul(all_queries, all_keys.transpose(-2, -1))
        attention_scores = attention_scores / (self.hidden_size ** 0.5)
        attention_probs = torch.softmax(attention_scores, dim=-1)
        
        # 注意力加权
        context = torch.matmul(attention_probs, all_values)
        
        # 模态间融合
        fused = torch.mean(context, dim=1)
        
        return fused
        
    def _create_query(self, features: torch.Tensor) -> torch.Tensor:
        """创建查询向量"""
        return nn.Linear(features.shape[-1], self.hidden_size)(features)
        
    def _create_key(self, features: torch.Tensor) -> torch.Tensor:
        """创建键向量"""
        return nn.Linear(features.shape[-1], self.hidden_size)(features)
        
    def _create_value(self, features: torch.Tensor) -> torch.Tensor:
        """创建值向量"""
        return nn.Linear(features.shape[-1], self.hidden_size)(features)