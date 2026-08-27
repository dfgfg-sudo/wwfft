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
        self.text_widget.insert(tk.END, msg + '\n')
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
        """处理多种输入格式：文件、文件夹、ZIP压缩包"""
        path = Path(input_path)
        
        if path.suffix == '.zip':
            self._handle_zip(path)
        elif path.is_dir():
            self._process_folder(path)
        else:
            self._process_file(path)
            
        return self._clean_data()
    
    def _handle_zip(self, zip_path):
        """解压并处理ZIP文件"""
        extract_to = zip_path.parent / f"extract_{zip_path.stem}"
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        self._process_folder(extract_to)
    
    def _process_folder(self, folder):
        """递归处理文件夹"""
        for item in folder.rglob('*'):
            if item.is_file() and item.suffix in ConfigManager.SUPPORTED_EXTS:
                self._process_file(item)
    
    def _process_file(self, file_path):
        """分派文件处理"""
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
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _process_pdf(self, file_path):
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def _process_excel(self, file_path):
        return pd.read_excel(file_path).to_dict()
    
    def _process_image(self, file_path):
        img = Image.open(file_path)
        return self.img_transform(img)
    
    def _process_code(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _hash_data(self, data):
        return hashlib.md5(str(data).encode()).hexdigest()
    
    def _clean_data(self):
        hashes = set()
        unique_data = []
        for item in self.raw_data:
            if item['hash'] not in hashes:
                hashes.add(item['hash'])
                unique_data.append(item)
        
        self.clean_data = []
        for item in unique_data:
            cleaned = self._clean_content(item['content'], item['type'])
            if cleaned:
                self.clean_data.append({
                    **item,
                    'cleaned_content': cleaned,
                    'labels': self._auto_label(item)
                })
        
        for item in self.clean_data:
            item['labels'] = self._auto_label(item)
        
        return self._split_data()
    
    def _clean_content(self, content, data_type):
        if data_type in ['txt', 'py', 'json', 'pdf', 'docx']:
            cleaned = re.sub(r'[^\x00-\x7F]+', '', str(content))
            return '\n'.join([line.strip() for line in cleaned.splitlines() if line.strip()])
        elif data_type == 'csv':
            return pd.read_csv(content).dropna().to_dict()
        return content
    
    def _auto_label(self, item):
        return {'file_type': item['type']}
    
    def _split_data(self, test_size=0.2):
        train, valid = train_test_split(
            self.clean_data, 
            test_size=test_size,
            random_state=42
        )
        return {
            'train': Dataset.from_pandas(pd.DataFrame(train)),
            'valid': Dataset.from_pandas(pd.DataFrame(valid))
        }

class ModelTrainer:
    def __init__(self, base_model):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, self.tokenizer = self._load_model(base_model)
        self._configure_peft()
    
    def _load_model(self, model_path):
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            if tokenizer.pad_token is None:
                tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            return model, tokenizer
        except Exception as e:
            logging.error(f"Model loading failed: {str(e)}")
            raise
    
    def _configure_peft(self):
        peft_config = LoraConfig(
            r=8,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            task_type="CAUSAL_LM"
        )
        self.model = get_peft_model(self.model, peft_config)
        self.model.print_trainable_parameters()
    
    def _tokenize_data(self, examples):
        return self.tokenizer(
            examples["cleaned_content"],
            padding="max_length",
            truncation=True,
            max_length=512
        )
    
    def train(self, dataset, epochs=3):
        train_dataset = dataset['train'].map(self._tokenize_data, batched=True)
        valid_dataset = dataset['valid'].map(self._tokenize_data, batched=True)
        
        training_args = TrainingArguments(
            output_dir=ConfigManager.PATHS['output'],
            num_train_epochs=epochs,
            per_device_train_batch_size=2,
            logging_steps=10,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            fp16=torch.cuda.is_available()
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=valid_dataset,
            data_collator=default_data_collator
        )
        
        trainer.train()
        return trainer

class TrainingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Trainer Pro 4.0")
        self.geometry("1200x800")
        self.trainer = None
        self.current_dataset = None
        self._setup_ui()
        self._setup_logging()
        
    def _setup_logging(self):
        gui_handler = GUILogHandler(self.log_area)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
    
    def _setup_ui(self):
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(ctrl_frame, text="📁 加载数据", command=self.load_data).pack(side=tk.LEFT)
        ttk.Button(ctrl_frame, text="🚀 开始训练", command=self.start_training).pack(side=tk.LEFT)
        ttk.Button(ctrl_frame, text="💾 导出模型", command=self.export_model).pack(side=tk.LEFT)
        
        stats_frame = ttk.LabelFrame(self, text="数据统计")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.data_stats = {
            'total': tk.StringVar(value="总数据量: 0"),
            'types': tk.StringVar(value="文件类型: "),
            'status': tk.StringVar(value="状态: 就绪")
        }
        for var in self.data_stats.values():
            ttk.Label(stats_frame, textvariable=var).pack(side=tk.LEFT, padx=20)
        
        self.progress = ttk.Progressbar(self, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def log(self, message, level='info'):
        self.log_area.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level.upper()} - {message}\n")
        self.log_area.see(tk.END)
    
    def _update_stats(self, total):
        types = ', '.join(set([item['type'] for item in self.current_dataset]))
        self.data_stats['total'].set(f"总数据量: {total}")
        self.data_stats['types'].set(f"文件类型: {types}")
        self.data_stats['status'].set("状态: 数据加载完成")
    
    def load_data(self):
        folder_path = filedialog.askdirectory(title="选择数据文件夹")
        if folder_path:
            self.process_data(folder_path)
    
    def process_data(self, folder_path):
        def _process():
            try:
                preprocessor = DataPreprocessor()
                preprocessor.process_input(folder_path)
                self.current_dataset = preprocessor.clean_data
                self.after(0, self._update_stats, len(preprocessor.clean_data))
                self.after(0, self.log, "数据预处理完成！")
            except Exception as e:
                self.after(0, self.log, f"数据处理错误: {str(e)}", 'error')
        
        threading.Thread(target=_process, daemon=True).start()
    
    def start_training(self):
        if not self.current_dataset:
            self.after(0, messagebox.showerror, "错误", "请先加载训练数据！")
            return
        
        def _train():
            try:
                self.after(0, self.log, "开始模型训练...")
                self.trainer = ModelTrainer(ConfigManager.PATHS['model'])
                self.trainer.train(self.current_dataset, epochs=3)
                self.after(0, self.log, "训练完成！", 'success')
            except Exception as e:
                self.after(0, self.log, f"训练失败: {str(e)}", 'error')
        
        threading.Thread(target=_train, daemon=True).start()
    
    def export_model(self):
        if self.trainer is None:
            messagebox.showerror("错误", "没有训练好的模型可导出！")
            return
        export_dir = filedialog.askdirectory(title="选择导出目录")
        if export_dir:
            self.trainer.model.save_pretrained(export_dir)
            self.trainer.tokenizer.save_pretrained(export_dir)
            self.log(f"模型已导出到 {export_dir}", 'success')

if __name__ == "__main__":
    ConfigManager.init_paths()
    app = TrainingGUI()
    app.mainloop()