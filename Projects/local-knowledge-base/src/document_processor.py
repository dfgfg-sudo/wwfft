#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理器模块
支持多种文档格式的处理和分块
"""

import os
import re
from langchain_community.document_loaders import (
    PyPDFLoader,
    DocxLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size=512, chunk_overlap=100):
        """初始化文档处理器"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化文本分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path):
        """加载单个文档"""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif ext == '.docx':
                loader = DocxLoader(file_path)
            elif ext == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            elif ext in ['.txt', '.log', '.csv']:
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                return None
            
            documents = loader.load()
            return documents
        except Exception as e:
            print(f"加载文档失败: {file_path}, 错误: {str(e)}")
            return None
    
    def load_documents(self, directory):
        """加载目录中的所有文档"""
        all_documents = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                documents = self.load_document(file_path)
                if documents:
                    all_documents.extend(documents)
        
        return all_documents
    
    def split_documents(self, documents):
        """分块文档"""
        if not documents:
            return []
        
        # 分块文档
        chunks = self.text_splitter.split_documents(documents)
        
        # 清理分块内容
        cleaned_chunks = []
        for chunk in chunks:
            # 清理空白字符
            cleaned_content = re.sub(r'\s+', ' ', chunk.page_content).strip()
            if cleaned_content:
                chunk.page_content = cleaned_content
                cleaned_chunks.append(chunk)
        
        return cleaned_chunks
    
    def process_directory(self, directory):
        """处理目录中的所有文档"""
        # 加载文档
        documents = self.load_documents(directory)
        
        # 分块文档
        chunks = self.split_documents(documents)
        
        return chunks
