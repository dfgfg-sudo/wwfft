# 📝 文本分类解决方案

## 📋 概述

基于HuggingFace的完整文本分类解决方案，支持多语言文本分类、情感分析、主题识别等任务。

---

## 🔧 环境配置

### 必需依赖

| 库名 | 版本 | 用途 |
|------|------|------|
| torch | >=2.0 | 深度学习框架 |
| transformers | >=4.30 | HuggingFace模型 |
| datasets | >=2.13 | 数据集处理 |
| scikit-learn | >=1.3 | 评估指标 |
| pandas | >=2.0 | 数据处理 |

### 安装命令

```bash
pip install torch transformers datasets scikit-learn pandas numpy
```


## 🚀 完整实现代码

### 1. 导入必要库

```python
import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    set_seed
)
from datasets import Dataset
```

### 2. 数据预处理

```python
class DataProcessor:
    """数据预处理处理器"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    def load_data(self, file_path):
        """加载CSV数据"""
        df = pd.read_csv(file_path)
        return df
    
    def preprocess_function(self, examples):
        """文本预处理函数"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512,
            return_overflowing_tokens=False
    
    def create_dataset(self, df):
        """创建HuggingFace Dataset"""
        # 标签编码
        label_mapping = {label: idx for idx, label in enumerate(df["label"].unique())}
        df["label"] = df["label"].map(label_mapping)
        
        # 转换为Dataset
        dataset = Dataset.from_pandas(df)
        
        # 分词处理
        tokenized_dataset = dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=["text"]
        
        return tokenized_dataset, label_mapping
```

### 3. 模型训练

```python
class TextClassifier:
    """文本分类器"""
    
    def __init__(self, model_name="bert-base-chinese", num_labels=10):
        self.model_name = model_name
        self.num_labels = num_labels
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        ).to(self.device)
    
    def train(self, train_dataset, eval_dataset, output_dir="./results"):
        """训练模型"""
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=5,
            logging_dir="./logs",
            logging_steps=100,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            weight_decay=0.01,
            fp16=True,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy"
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics
        
        trainer.train()
        return trainer
    
    @staticmethod
    def compute_metrics(eval_pred):
        """计算评估指标"""
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        acc = accuracy_score(labels, predictions)
        return {"accuracy": acc}
```

### 4. 推理预测

```python
class Predictor:
    """预测器"""
    
    def __init__(self, model_path, tokenizer_path=None):
        if tokenizer_path is None:
            tokenizer_path = model_path
        
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
        
    def predict(self, text):
        """单条文本预测"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt"
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=1).item()
        
        return prediction
    
    def predict_batch(self, texts):
        """批量文本预测"""
            texts,
        
            predictions = torch.argmax(logits, dim=1).tolist()
        
        return predictions
```


## 📊 支持的模型

| 模型名称 | 语言 | 适用场景 |
|----------|------|----------|
| bert-base-chinese | 中文 | 通用文本分类 |
| roberta-base-chinese | 中文 | 通用文本分类 |
| chinese-roberta-wwm-ext | 中文 | 通用文本分类 |
| albert-base-chinese | 中文 | 轻量级分类 |
| electra-base-discriminator | 中文 | 判别式任务 |
| bert-base-multilingual-cased | 多语言 | 多语言分类 |


## 🔄 完整工作流程

```mermaid
flowchart LR
    A[加载数据] --> B[数据预处理]
    B --> C[划分数据集]
    C --> D[加载预训练模型]
    D --> E[训练模型]
    E --> F[评估模型]
    F --> G[保存模型]
    G --> H[推理预测]
```


## 📈 评估指标

| 指标 | 计算方式 | 说明 |
|------|----------|------|
| Accuracy | 正确预测数/总样本数 | 总体准确率 |
| Precision | TP/(TP+FP) | 精确率 |
| Recall | TP/(TP+FN) | 召回率 |
| F1-Score | 2*P*R/(P+R) | 综合指标 |
| Macro F1 | 各类F1的算术平均 | 类别不平衡时更适用 |


## 📎 相关文档

- [多模态AI训练系统](04_MULTIMODAL_SYSTEM.md) - 超融合训练平台
- [系统架构设计](10_SYSTEM_ARCHITECTURE.md) - 完整技术栈描述