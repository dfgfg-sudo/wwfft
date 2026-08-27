"""
import os
import json
import logging
import torch
import zipfile
import hashlib
import threading
import re
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from transformers import (
    AutoTokenizer,
    AutoConfig,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    default_data_collator
)
from peft import LoraConfig, get_peft_model
from PIL import Image
import pandas as pd
import docx
import PyPDF2
import chardet
from torchvision import transforms
from sklearn.model_selection import train_test_split
from datasets import Dataset
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("training.log"), logging.StreamHandler()]
)

class GUILogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\\n')
        self.text_widget.see(tk.END)

class ConfigManager:
    PATHS = {
        'model': Path('model'),
        'data': Path('data'),
        'output': Path('outputs')
    }
    
    SUPPORTED_EXTS = ('.txt', '.csv', '.json', '.docx', '.pdf', 
                     '.xlsx', '.png', '.jpg', '.zip', '.py')
    
    @classmethod
    def init_paths(cls):
        for p in cls.PATHS.values():
            p.mkdir(exist_ok=True, parents=True)

class DataPreprocessor:
    def __init__(self):
        self.raw_data = []
        self.clean_data = []
        self._init_image_transforms()
        
    def _init_image_transforms(self):
        self.img_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def process_input(self, input_path):
        \"\"\"处理多种输入格式：文件、文件夹、ZIP压缩包\"\"\"
        path = Path(input_path)
        
        if path.suffix == '.zip':
            self._handle_zip(path)
        elif path.is_dir():
            self._process_folder(path)
        else:
            self._process_file(path)
            
        return self._clean_data()
    
    def _handle_zip(self, zip_path):
        \"\"\"解压并处理ZIP文件\"\"\"
        extract_to = zip_path.parent / f"extract_{zip_path.stem}"
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        self._process_folder(extract_to)
    
    def _process_folder(self, folder):
        \"\"\"递归处理文件夹\"\"\"
        for item in folder.rglob('*'):
            if item.is_file() and item.suffix in ConfigManager.SUPPORTED_EXTS:
                self._process_file(item)
    
    def _process_file(self, file_path):
        \"\"\"分派文件处理\"\"\"
        try:
            ext = file_path.suffix.lower()
            handler = {
                '.txt': self._process_text,
                '.csv': self._process_csv,
                '.json': self._process_json,
                '.docx': self._process_docx,
                '.pdf': self._process_pdf,
                '.xlsx': self._process_excel,
                '.png': self._process_image,
                '.jpg': self._process_image,
                '.py': self._process_code
            }.get(ext, lambda x: None)
            
            if handler:
                data = handler(file_path)
                if data is not None:
                    self.raw_data.append({
                        'content': data,
                        'path': str(file_path),
                        'type': ext[1:],
                        'hash': self._hash_data(str(data))
                    })
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
    
    def _process_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _process_csv(self, file_path):
        return pd.read_csv(file_path).to_dict()
    
    def _process_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _process_docx(self, file_path):
        doc = docx.Document(file_path)
        return "\\n".join([para.text for para in doc.paragraphs])
    
    def _process_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                textAI Trainer Pro 4.0 – 完整项目文档（最终整合版）

本文档整合了全部对话历史中的代码、架构图、流程说明及功能拓展，严格保留原文格式，修复所有错误，并进行了精致排版。
项目全称：AI Trainer Pro 4.0 – 多模态智能训练系统
核心原则：无变动保留原文内容，仅修复错误，确保完整可运行。

---

目录

1. 完整可运行代码
2. 完整系统架构图（Mermaid）
3. 数据处理流程图（Mermaid）
4. 系统功能与兴趣点深度融合
5. 项目核心价值总结

---

1. 完整可运行代码
"""
