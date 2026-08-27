#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嵌入模型模块
使用DeepSeek中文嵌入模型
"""

import os
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        """初始化嵌入模型"""
        # 使用DeepSeek中文嵌入模型
        self.model_name = "deepseek-ai/deepseek-embedding-chinese-base-v1"
        self.cache_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'models'
        )
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 加载模型
        self.model = SentenceTransformer(
            self.model_name,
            cache_folder=self.cache_dir,
            device="cpu"  # 确保在CPU上运行，完全离线
        )
    
    def embed(self, text):
        """生成文本嵌入向量"""
        if not text or not isinstance(text, str):
            return []
        
        # 生成嵌入
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts):
        """批量生成文本嵌入向量"""
        if not texts or not isinstance(texts, list):
            return []
        
        # 批量生成嵌入
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
