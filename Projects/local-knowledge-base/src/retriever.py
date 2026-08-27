#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索器模块
管理向量数据库和执行相似度搜索
"""

import os
import json
import faiss
import numpy as np

class Retriever:
    def __init__(self, embedding_model):
        """初始化检索器"""
        self.embedding_model = embedding_model
        self.index = None
        self.documents = []
    
    def create_index(self, embeddings):
        """创建FAISS索引"""
        if not embeddings:
            return None
        
        # 转换为numpy数组
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        # 创建FAISS索引
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)
        
        return self.index
    
    def add_documents(self, documents):
        """添加文档到检索器"""
        if not documents:
            return
        
        # 提取文档内容
        texts = [doc.page_content for doc in documents]
        
        # 生成嵌入
        embeddings = self.embedding_model.embed_batch(texts)
        
        # 创建索引
        self.create_index(embeddings)
        
        # 存储文档
        self.documents = []
        for doc in documents:
            self.documents.append({
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'unknown')
            })
    
    def search(self, query, k=3, score_threshold=0.3):
        """搜索相似文档"""
        if not self.index or not self.documents:
            return []
        
        # 生成查询嵌入
        query_embedding = self.embedding_model.embed(query)
        if not query_embedding:
            return []
        
        # 转换为numpy数组
        query_embedding_np = np.array([query_embedding], dtype=np.float32)
        
        # 执行搜索
        distances, indices = self.index.search(query_embedding_np, k)
        
        # 处理结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                # 计算相似度（1 - 距离）
                similarity = 1.0 / (1.0 + distances[0][i])
                
                if similarity >= score_threshold:
                    results.append({
                        'content': self.documents[idx]['content'],
                        'source': self.documents[idx]['source'],
                        'score': similarity
                    })
        
        return results
    
    def save(self, save_path):
        """保存检索器"""
        if not self.index:
            return False
        
        try:
            # 保存FAISS索引
            index_path = os.path.join(save_path, 'index.faiss')
            faiss.write_index(self.index, index_path)
            
            # 保存文档
            docs_path = os.path.join(save_path, 'documents.json')
            with open(docs_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存检索器失败: {str(e)}")
            return False
    
    def load(self, load_path):
        """加载检索器"""
        try:
            # 加载FAISS索引
            index_path = os.path.join(load_path, 'index.faiss')
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
            else:
                return False
            
            # 加载文档
            docs_path = os.path.join(load_path, 'documents.json')
            if os.path.exists(docs_path):
                with open(docs_path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            else:
                return False
            
            return True
        except Exception as e:
            print(f"加载检索器失败: {str(e)}")
            return False
