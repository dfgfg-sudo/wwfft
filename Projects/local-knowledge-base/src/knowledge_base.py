#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库主模块
协调各个组件的工作，包括构建、查询和更新知识库
"""

import os
import shutil

class KnowledgeBase:
    def __init__(self, name, document_processor, embedding_model, retriever):
        """初始化知识库"""
        self.name = name
        self.document_processor = document_processor
        self.embedding_model = embedding_model
        self.retriever = retriever
        
        # 知识库存储路径
        self.base_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data', 'knowledge_bases'
        )
        self.kb_dir = os.path.join(self.base_dir, name)
        
        # 创建知识库目录
        os.makedirs(self.kb_dir, exist_ok=True)
    
    def build(self, documents_path):
        """构建知识库"""
        # 处理文档
        chunks = self.document_processor.process_directory(documents_path)
        
        if not chunks:
            raise Exception("没有找到可处理的文档")
        
        # 添加文档到检索器
        self.retriever.add_documents(chunks)
        
        # 保存检索器
        self.retriever.save(self.kb_dir)
    
    def query(self, query, k=3, score_threshold=0.3):
        """查询知识库"""
        # 加载检索器
        if not self.retriever.load(self.kb_dir):
            raise Exception("知识库未找到或损坏")
        
        # 执行搜索
        results = self.retriever.search(query, k=k, score_threshold=score_threshold)
        
        return results
    
    def update(self, documents_path):
        """更新知识库"""
        # 加载现有检索器
        if not self.retriever.load(self.kb_dir):
            # 如果知识库不存在，创建新的
            self.build(documents_path)
            return
        
        # 处理新文档
        new_chunks = self.document_processor.process_directory(documents_path)
        
        if not new_chunks:
            raise Exception("没有找到可处理的文档")
        
        # 获取现有文档
        existing_docs = self.retriever.documents
        
        # 合并文档
        all_chunks = []
        
        # 去重
        existing_contents = set()
        for doc in existing_docs:
            existing_contents.add(doc['content'])
        
        # 添加新文档
        for chunk in new_chunks:
            if chunk.page_content not in existing_contents:
                all_chunks.append(chunk)
                existing_contents.add(chunk.page_content)
        
        # 如果有新文档，更新知识库
        if all_chunks:
            # 添加所有文档（包括现有和新文档）
            self.retriever.add_documents(new_chunks)
            
            # 保存更新后的检索器
            self.retriever.save(self.kb_dir)
    
    def delete(self):
        """删除知识库"""
        if os.path.exists(self.kb_dir):
            shutil.rmtree(self.kb_dir)
            return True
        return False
    
    def exists(self):
        """检查知识库是否存在"""
        return os.path.exists(self.kb_dir)
