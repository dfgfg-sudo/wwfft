#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级本地知识库系统
✅ 完全离线 - 隐私数据不出本地
✅ 低内存占用 - 优化资源使用
✅ 零成本 - 全部开源免费
"""

import os
import sys
import click

# 导入核心模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@click.group()
def cli():
    """轻量级本地知识库系统"""
    pass

@cli.command()
@click.option('--name', '-n', default='my_knowledge_base', help='知识库名称')
@click.option('--query', '-q', required=True, help='查询内容')
def query(name, query):
    """查询知识库"""
    try:
        # 延迟导入以减少内存占用
        from src.knowledge_base import KnowledgeBase
        from src.embedding import EmbeddingModel
        from src.retriever import Retriever
        
        # 加载知识库
        embedding_model = EmbeddingModel()
        retriever = Retriever(embedding_model)
        kb = KnowledgeBase(name, None, embedding_model, retriever)
        
        # 执行查询
        results = kb.query(query, k=3, score_threshold=0.3)
        
        # 显示结果
        print("\n查询结果:")
        for i, result in enumerate(results, 1):
            print(f"结果 {i}")
            print(f"文件: {result['source']}")
            print(f"相似度: {result['score']:.4f}")
            print(f"内容: {result['content'][:300]}...")
            print("-" * 80)
            
    except Exception as e:
        print(f"错误: {str(e)}")

@cli.command()
def list_kbs():
    """列出所有知识库"""
    print("\n所有知识库:")
    
    kb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'knowledge_bases')
    if os.path.exists(kb_dir):
        kbs = os.listdir(kb_dir)
        for kb in kbs:
            print(f"✓ {kb}")
    else:
        print("暂无知识库")

if __name__ == '__main__':
    cli()
