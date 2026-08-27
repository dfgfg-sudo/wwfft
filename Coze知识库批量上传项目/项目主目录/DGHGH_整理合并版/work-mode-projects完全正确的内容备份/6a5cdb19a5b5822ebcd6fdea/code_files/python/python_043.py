# -*- coding: utf-8 -*-
"""
🧠 量子增强模型训练引擎
✅ 支持多模态Transformer模型训练
"""

import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    """量子增强模型训练引擎"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        logger.info(f"使用设备: {self.device}")
        logger.info(f"初始模型: {model_name}")
    
    def initialize_model(self):
        """初始化模型"""
        try:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model.to(self.device)
            logger.info(f"模型加载成功: {self.model_name}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def prepare_data(self, data: List[Dict[str, Any]]) -> Dataset:
        """准备训练数据"""
        texts = []
        
        for item in data:
            if item['type'] == 'text':
                texts.append(item['content'])
            elif item['type'] in ['json', 'csv', 'excel']:
                # 将结构化数据转换为文本
                text = self._structure_to_text(item)
                texts.append(text)
        
        # 创建数据集
        dataset = Dataset.from_dict({"text": texts})
        
        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=512
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        logger.info(f"数据准备完成: {len(texts)} 条文本")
        return tokenized_dataset
    
    def train(self, dataset: Dataset, training_args: Optional[Dict] = None):
        """训练模型"""
        if self.model is None:
            self.initialize_model()
        
        # 默认训练参数
        default_args = {
            "output_dir": "./models",
            "num_train_epochs": 3,
            "per_device_train_batch_size": 4,
            "warmup_steps": 500,
            "weight_decay": 0.01,
            "logging_dir": "./logs",
            "logging_steps": 10,
            "save_steps": 500,
            "eval_steps": 500,
            "save_total_limit": 2,
        }
        
        if training_args:
            default_args.update(training_args)
        
        # 创建TrainingArguments
        args = TrainingArguments(**default_args)
        
        # 数据收集器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # 创建Trainer
        self.trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=dataset,
            data_collator=data_collator,
        )
        
        # 开始训练
        logger.info("开始模型训练...")
        self.trainer.train()
        
        # 保存模型
        self.trainer.save_model()
        logger.info(f"模型训练完成，保存到: {default_args['output_dir']}")
    
    def evaluate(self, dataset: Dataset) -> Dict[str, float]:
        """评估模型"""
        if self.trainer is None:
            raise ValueError("请先训练模型")
        
        results = self.trainer.evaluate(dataset)
        logger.info(f"评估结果: {results}")
        return results
    
    def generate_text(self, prompt: str, max_length: int = 100) -> str:
        """生成文本"""
        if self.model is None or self.tokenizer is None:
            self.initialize_model()
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    
    def _structure_to_text(self, item: Dict[str, Any]) -> str:
        """将结构化数据转换为文本"""
        if item['type'] == 'json':
            return self._json_to_text(item['data'])
        elif item['type'] == 'csv':
            return self._csv_to_text(item['data'])
        elif item['type'] == 'excel':
            return self._excel_to_text(item['sheets'])
        else:
            return str(item)
    
    def _json_to_text(self, data: Any) -> str:
        """JSON转文本"""
        def process_value(value, indent=0):
            if isinstance(value, dict):
                lines = []
                for k, v in value.items():
                    lines.append(f"{'  ' * indent}{k}: {process_value(v, indent + 1)}")
                return "\n".join(lines)
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], (dict, list)):
                    return f"[列表，共{len(value)}项]"
                else:
                    return str(value[:10]) + ("..." if len(value) > 10 else "")
            else:
                return str(value)
        
        return process_value(data)
    
    def _csv_to_text(self, data: List[Dict]) -> str:
        """CSV转文本"""
        if not data:
            return ""
        
        lines = []
        # 表头
        headers = list(data[0].keys())
        lines.append(" | ".join(headers))
        lines.append("-" * len(" | ".join(headers)))
        
        # 数据行（最多10行）
        for row in data[:10]:
            line = " | ".join(str(row.get(h, ""))[:50] for h in headers)
            lines.append(line)
        
        if len(data) > 10:
            lines.append(f"... 还有 {len(data) - 10} 行")
        
        return "\n".join(lines)
    
    def _excel_to_text(self, sheets: Dict[str, Any]) -> str:
        """Excel转文本"""
        lines = ["Excel文件内容:"]
        
        for sheet_name, sheet_data in sheets.items():
            lines.append(f"\n工作表: {sheet_name}")
            lines.append(self._csv_to_text(sheet_data['data'][:5]))  # 每个表取前5行
        
        return "\n".join(lines)