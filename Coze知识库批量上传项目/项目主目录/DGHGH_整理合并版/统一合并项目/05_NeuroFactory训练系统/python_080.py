#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态数据处理模块
"""
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
from pathlib import Path
import logging

logger = logging.getLogger("BunnySystem")

class MultiModalProcessor:
    """多模态数据处理核心类"""
    
    @staticmethod
    def load_text(filepath):
        """加载文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"成功加载文本文件: {filepath}")
            return content
        except Exception as e:
            logger.error(f"加载文本文件失败 {filepath}: {str(e)}")
            return ""
    
    @staticmethod
    def load_image(filepath):
        """加载图像文件"""
        try:
            image = Image.open(filepath).convert('RGB')
            logger.info(f"成功加载图像文件: {filepath}")
            return image
        except Exception as e:
            logger.error(f"加载图像文件失败 {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def load_pdf(filepath):
        """加载PDF文件"""
        try:
            doc = fitz.open(filepath)
            text = ""
            for page_num, page in enumerate(doc):
                text += f"--- Page {page_num + 1} ---\n"
                text += page.get_text() + "\n"
            doc.close()
            logger.info(f"成功加载PDF文件: {filepath}")
            return text
        except Exception as e:
            logger.error(f"加载PDF文件失败 {filepath}: {str(e)}")
            return ""
    
    @staticmethod
    def load_table(filepath):
        """加载表格文件"""
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                logger.warning(f"不支持的表格格式: {filepath}")
                return None
            logger.info(f"成功加载表格文件: {filepath}")
            return df
        except Exception as e:
            logger.error(f"加载表格文件失败 {filepath}: {str(e)}")
            return None
    
    def process_file(self, filepath):
        """统一文件处理方法"""
        filepath = Path(filepath)
        ext = filepath.suffix.lower()
        
        if ext in ['.txt', '.md']:
            return self.load_text(filepath)
        elif ext in ['.jpg', '.png', '.jpeg']:
            return self.load_image(filepath)
        elif ext == '.pdf':
            return self.load_pdf(filepath)
        elif ext in ['.csv', '.xlsx']:
            return self.load_table(filepath)
        else:
            logger.warning(f"不支持的文件类型: {ext}")
            return None