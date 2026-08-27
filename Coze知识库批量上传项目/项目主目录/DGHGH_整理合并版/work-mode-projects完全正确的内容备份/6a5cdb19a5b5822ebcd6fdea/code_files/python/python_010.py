#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                   全栈AI工厂 - 完整合并修复版 v16.0
================================================================================
整合模块：
1. Transformer本地数据智能投喂系统
2. 股票智能分析系统（含数据库、量化指标、Tkinter GUI）
3. 全栈式AI系统（FastAPI、模型路由、安全、LLM集成）
4. Bunny模型全栈式智能训练系统（知识蒸馏、自动修复、分布式）
5. Neuro Factory（PyQt5训练界面、代码生成、加密）
6. AI Factory（监控、数据监控、加密、训练）
7. 企业级智能文件管理（Flask、SQLAlchemy）

所有代码严格保留原文注释与结构，仅修复语法错误、缺失导入和类名冲突。
================================================================================
"""

# ====================== 全局导入 ======================
import os
import sys
import json
import csv
import time
import pickle
import hashlib
import logging
import sqlite3
import requests
import webbrowser
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from collections import defaultdict
from threading import Thread, Event
from cryptography.fernet import Fernet
import networkx as nx
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset as TorchDataset

# 深度学习核心
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    BitsAndBytesConfig, pipeline, AutoConfig, T5ForConditionalGeneration
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset, concatenate_datasets, load_from_disk

# Web框架
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

# GUI - PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QLabel, QLineEdit, QTabWidget,
    QSlider, QMessageBox, QProgressBar, QGroupBox, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer

# GUI - Tkinter (股票系统)
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# ====================== 日志系统 ======================
def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(f'logs/system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("UnifiedSystem")

logger = init_logging()

# ====================== 一、Transformer本地数据智能投喂 ======================
SYSTEM_CONFIG = {
    "LOCAL_MODEL_PATH": r"C:\Users\Administrator\Documents\uytrertrt\Bunny-v1_0-3B\neuro_data",
    "DATA_DIRS": ["data", "knowledge", "dialogues"],
    "OUTPUT_DIR": "transformer_output",
    "SUPPORTED_MODES": ["text", "image", "audio"],
    "AUTO_TRAIN_THRESHOLD": 20,
    "MAX_SEQ_LENGTH": 512
}

class TextAugmentor:
    def augment(self, text: str) -> str:
        return text.replace(".", "。").replace("!", "！")

class ImageAugmentor:
    def augment(self, image_path: str) -> str:
        logger.info(f"增强图像: {image_path}")
        return image_path

class AudioAugmentor:
    def augment(self, audio_path: str) -> str:
        logger.info(f"增强音频: {audio_path}")
        return audio_path

class MultiModalAugmentor:
    def __init__(self):
        self.augmentors = {"text": TextAugmentor(), "image": ImageAugmentor(), "audio": AudioAugmentor()}
    def process(self, data_type: str, content: str) -> str:
        return self.augmentors[data_type].augment(content)

class TransformerDataset(TorchDataset):
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.inputs = []
        self.labels = []
    def add_sample(self, text: str, label: int = -1):
        enc = self.tokenizer(text, padding="max_length", truncation=True,
                             max_length=self.max_length, return_tensors="pt")
        self.inputs.append(enc["input_ids"].squeeze())
        if label != -1:
            self.labels.append(torch.tensor(label))
    def __len__(self):
        return len(self.inputs)
    def __getitem__(self, idx):
        item = {"input_ids": self.inputs[idx], "attention_mask": torch.ones_like(self.inputs[idx])}
        if self.labels:
            item["labels"] = self.labels[idx]
        return item

class DataProcessor:
    def __init__(self):
        self.augmentor = MultiModalAugmentor()
        self.tokenizer = AutoTokenizer.from_pretrained(SYSTEM_CONFIG["LOCAL_MODEL_PATH"])
        self.dataset = TransformerDataset(self.tokenizer, SYSTEM_CONFIG["MAX_SEQ_LENGTH"])
    def process_file(self, file_path: Path, data_type: str):
        content = self._load_content(file_path, data_type)
        augmented = self.augmentor.process(data_type, content)
        self._parse_to_dataset(augmented, data_type)
    def _load_content(self, path: Path, data_type: str) -> str:
        if data_type == "text":
            with open(path, "r", encoding="utf-8") as f: return f.read()
        elif data_type == "image": return str(path)
        elif data_type == "audio": return str(path)
        elif data_type in ["json", "csv"]:
            with open(path, "r", encoding="utf-8") as f:
                return json.dumps(self._parse_structured(f.read(), data_type))
    def _parse_structured(self, content: str, data_type: str):
        if data_type == "json": return json.loads(content)
        elif data_type == "csv": return list(csv.DictReader(content.splitlines()))
    def _parse_to_dataset(self, content: str, data_type: str):
        if data_type == "text":
            self.dataset.add_sample(content, label=0)

class TransformerModelRouter:
    def __init__(self):
        self.model_map = {
            "classification": AutoModelForSequenceClassification.from_pretrained(
                SYSTEM_CONFIG["LOCAL_MODEL_PATH"], num_labels=2),
            "generation": T5ForConditionalGeneration.from_pretrained(
                SYSTEM_CONFIG["LOCAL_MODEL_PATH"]),
            "causal_lm": AutoModelForCausalLM.from_pretrained(
                SYSTEM_CONFIG["LOCAL_MODEL_PATH"])
        }
    def get_model(self, task_type: str):
        return self.model_map[task_type]

class TransformerTrainer:
    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset
        self.training_args = TrainingArguments(
            output_dir=SYSTEM_CONFIG["OUTPUT_DIR"],
            num_train_epochs=3,
            per_device_train_batch_size=8,
            warmup_steps=100,
            logging_dir=f"{SYSTEM_CONFIG['OUTPUT_DIR']}/logs",
            fp16=True,
            save_strategy="no"
        )
    def start_training(self):
        trainer = Trainer(model=self.model, args=self.training_args, train_dataset=self.dataset)
        trainer.train()
        logger.info(f"训练完成，模型保存至: {self.training_args.output_dir}")

class DataEventhandler(FileSystemEventHandler):
    def __init__(self, processor: DataProcessor, trainer: TransformerTrainer):
        self.processor = processor
        self.trainer = trainer
        self.data_count = 0
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            data_type = self._infer_data_type(file_path)
            if data_type in SYSTEM_CONFIG["SUPPORTED_MODES"]:
                logger.info(f"检测到新数据: {file_path}, 类型: {data_type}")
                self.processor.process_file(file_path, data_type)
                self.data_count += 1
                if self.data_count >= SYSTEM_CONFIG["AUTO_TRAIN_THRESHOLD"]:
                    self._trigger_training()
    def _infer_data_type(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in [".txt", ".json", ".csv"]: return "text"
        elif suffix in [".jpg", ".png"]: return "image"
        elif suffix in [".wav", ".mp3"]: return "audio"
        return "unknown"
    def _trigger_training(self):
        model_router = TransformerModelRouter()
        model = model_router.get_model("classification")
        trainer = TransformerTrainer(model, self.processor.dataset)
        trainer.start_training()
        self.data_count = 0

# ====================== 二、股票智能分析系统 ======================
class StockDatabase:
    def __init__(self, db_file='stock_system.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._initialize_db()
    def _initialize_db(self):
        tables = [
            '''CREATE TABLE IF NOT EXISTS stocks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL,
                volume INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''',
            '''CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, last_login DATETIME)''',
            '''CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)'''
        ]
        for t in tables:
            self.cursor.execute(t)
        self.conn.commit()
    def insert_stock_data(self, data):
        try:
            self.cursor.execute('''INSERT INTO stocks (symbol, open, high, low, close, volume)
                                 VALUES (?,?,?,?,?,?)''',
                                 (data['symbol'], data['open'], data['high'],
                                  data['low'], data['close'], data['volume']))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"DB insert error: {e}")
            return False
    def get_historical_data(self, symbol, limit=100):
        try:
            self.cursor.execute('''SELECT timestamp, open, high, low, close, volume
                                 FROM stocks WHERE symbol=? ORDER BY timestamp DESC LIMIT ?''', (symbol, limit))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"DB query error: {e}")
            return []
    def user_login(self, username, password):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''UPDATE users SET last_login = datetime('now')
                             WHERE username=? AND password=? RETURNING *''', (username, hashed))
        res = self.cursor.fetchone()
        self.conn.commit()
        return res
    def get_setting(self, key):
        self.cursor.execute('SELECT value FROM settings WHERE key=?', (key,))
        r = self.cursor.fetchone()
        return r[0] if r else None
    def save_setting(self, key, value):
        try:
            self.cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)', (key, value))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Save setting error: {e}")
            return False
    def __del__(self):
        if self.conn:
            self.conn.close()

class FinancialDataAPI:
    def __init__(self, db):
        self.db = db
        self.API_BASE = db.get_setting('api_base') or "https://api.example.com/finance"
    def fetch_market_data(self, symbol):
        try:
            resp = requests.get(f"{self.API_BASE}/realtime/{symbol}", timeout=10,
                                headers={'User-Agent': 'StockSystem/5.0'})
            resp.raise_for_status()
            data = resp.json()
            return self._parse_api_data(data, symbol)
        except:
            return self._generate_mock_data(symbol)
    def _parse_api_data(self, data, symbol):
        return {'symbol': symbol, 'open': data['ohlc']['open'], 'high': data['ohlc']['high'],
                'low': data['ohlc']['low'], 'close': data['ohlc']['close'], 'volume': data['volume']['total']}
    def _generate_mock_data(self, symbol):
        base = np.random.uniform(50,200)
        return {'symbol': symbol, 'open': round(base,2), 'high': round(base*1.05,2),
                'low': round(base*0.95,2), 'close': round(base*(1+np.random.uniform(-0.03,0.03)),2),
                'volume': np.random.randint(100000,500000)}

class QuantitativeAnalyzer:
    @staticmethod
    def analyze(df):
        df = df.copy()
        df['date'] = pd.to_datetime(df['timestamp'])
        df.set_index('date', inplace=True)
        df['MA5'] = df['close'].rolling(5).mean()
        df['MA20'] = df['close'].rolling(20).mean()
        df['RSI'] = QuantitativeAnalyzer._calculate_rsi(df['close'])
        df['MACD'], df['Signal'] = QuantitativeAnalyzer._calculate_macd(df['close'])
        df['Bollinger_Upper'], df['Bollinger_Lower'] = QuantitativeAnalyzer._calculate_bollinger(df['close'])
        report = {
            'current_price': df['close'].iloc[-1],
            'price_change_1d': df['close'].pct_change().iloc[-1] * 100,
            'volatility_7d': df['close'].pct_change().std() * np.sqrt(252),
            'volume_change': (df['volume'].iloc[-1] / df['volume'].mean() - 1) * 100,
            'rsi': df['RSI'].iloc[-1],
            'macd_crossover': df['MACD'].iloc[-1] > df['Signal'].iloc[-1],
            'bollinger_position': QuantitativeAnalyzer._get_bollinger_position(df)
        }
        return df, report
    @staticmethod
    def _calculate_rsi(series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/period).mean()
        avg_loss = loss.ewm(alpha=1/period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    @staticmethod
    def _calculate_macd(series, fast=12, slow=26, signal=9):
        ema_fast = series.ewm(span=fast).mean()
        ema_slow = series.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd, signal_line
    @staticmethod
    def _calculate_bollinger(series, window=20, num_std=2):
        sma = series.rolling(window).mean()
        std = series.rolling(window).std()
        return sma + (std * num_std), sma - (std * num_std)
    @staticmethod
    def _get_bollinger_position(df):
        last = df['close'].iloc[-1]
        upper = df['Bollinger_Upper'].iloc[-1]
        lower = df['Bollinger_Lower'].iloc[-1]
        if last > upper: return "突破上轨"
        if last < lower: return "突破下轨"
        return "轨道区间内"

# Tkinter 交易仪表盘
class TradingDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("智能量化交易终端 v5.0")
        self.geometry("1366x768")
        self.configure(bg='#F5F6F7')
        self.db = StockDatabase()
        self.api = FinancialDataAPI(self.db)
        self.analyzer = QuantitativeAnalyzer()
        self.current_symbol = 'AAPL'
        self.current_user = None
        self._init_login_window()
        self._create_menu()
    def _create_menu(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="导出数据", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "股票分析系统 v5.0"))
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        self.config(menu=menu_bar)
    def _init_login_window(self):
        self.login_window = tk.Toplevel(self)
        self.login_window.title("用户登录")
        self.login_window.geometry("300x200")
        self.login_window.grab_set()
        ttk.Label(self.login_window, text="用户名:").pack(pady=5)
        self.username_entry = ttk.Entry(self.login_window)
        self.username_entry.pack(pady=5)
        ttk.Label(self.login_window, text="密码:").pack(pady=5)
        self.password_entry = ttk.Entry(self.login_window, show="*")
        self.password_entry.pack(pady=5)
        ttk.Button(self.login_window, text="登录", command=self._login).pack(pady=10)
    def _login(self):
        user = self.db.user_login(self.username_entry.get(), self.password_entry.get())
        if user:
            self.current_user = user
            self.login_window.destroy()
            self._init_main_ui()
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    def _init_main_ui(self):
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X)
        ttk.Label(control_frame, text="股票代码:").grid(row=0, column=0)
        self.symbol_entry = ttk.Entry(control_frame, width=8)
        self.symbol_entry.grid(row=0, column=1, padx=5)
        self.symbol_entry.insert(0, self.current_symbol)
        buttons = [('刷新', self.refresh_data), ('实时', self.fetch_realtime),
                   ('分析', self.show_analysis), ('历史', self.show_history)]
        for col, (text, cmd) in enumerate(buttons, start=2):
            ttk.Button(control_frame, text=text, command=cmd).grid(row=0, column=col, padx=2)
        self.data_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=('Consolas',10), height=15)
        self.data_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.figure = plt.Figure(figsize=(10,5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.status_bar = ttk.Label(self, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.update_status("就绪")
        self.refresh_data()
    def update_status(self, msg):
        self.status_bar.config(text=f"状态: {msg}")
    def refresh_data(self):
        self.current_symbol = self.symbol_entry.get().upper()
        self.show_history()
        self.update_status(f"已刷新 {self.current_symbol}")
    def fetch_realtime(self):
        data = self.api.fetch_market_data(self.current_symbol)
        if self.db.insert_stock_data(data):
            self.refresh_data()
            self.update_status(f"实时数据已更新: {self.current_symbol}")
    def show_analysis(self):
        data = self.db.get_historical_data(self.current_symbol)
        if not data:
            messagebox.showwarning("警告", "无可用数据")
            return
        df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
        processed_df, report = self.analyzer.analyze(df)
        self.ax.clear()
        processed_df['close'].plot(ax=self.ax, label='收盘价', color='#1f77b4')
        processed_df['MA5'].plot(ax=self.ax, label='5日均线', linestyle='--')
        processed_df['MA20'].plot(ax=self.ax, label='20日均线', linestyle='--')
        processed_df['Bollinger_Upper'].plot(ax=self.ax, color='green', alpha=0.5)
        processed_df['Bollinger_Lower'].plot(ax=self.ax, color='red', alpha=0.5)
        self.ax.fill_between(processed_df.index, processed_df['Bollinger_Upper'],
                             processed_df['Bollinger_Lower'], color='gray', alpha=0.1)
        self.ax.set_title(f"{self.current_symbol} 技术分析")
        self.ax.legend()
        self.canvas.draw()
        # 显示报告窗口
        win = tk.Toplevel(self)
        win.title("分析报告")
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.insert(tk.END, f"当前价格: {report['current_price']:.2f}\n日涨跌幅: {report['price_change_1d']:.2f}%\nRSI: {report['rsi']:.1f}\nMACD信号: {'买入' if report['macd_crossover'] else '卖出'}")
        text.pack(fill=tk.BOTH, expand=True)
    def show_history(self):
        data = self.db.get_historical_data(self.current_symbol)
        self.data_display.delete(1.0, tk.END)
        if not data:
            self.data_display.insert(tk.END, "无历史数据")
            return
        headers = ["时间", "开盘", "最高", "最低", "收盘", "成交量"]
        self.data_display.insert(tk.END, "\t".join(headers) + "\n")
        for rec in reversed(data):
            self.data_display.insert(tk.END, f"{rec[0][:16]}\t{rec[1]:.2f}\t{rec[2]:.2f}\t{rec[3]:.2f}\t{rec[4]:.2f}\t{rec[5]:,}\n")
    def export_csv(self):
        data = self.db.get_historical_data(self.current_symbol)
        if not data:
            messagebox.showwarning("警告", "无数据可导出")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV文件","*.csv")])
        if path:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['时间戳','开盘','最高','最低','收盘','成交量'])
                for rec in data:
                    writer.writerow([rec[0], f"{rec[1]:.2f}", f"{rec[2]:.2f}", f"{rec[3]:.2f}", f"{rec[4]:.2f}", f"{rec[5]:,}"])
            messagebox.showinfo("导出成功", f"数据已导出至 {path}")

# ====================== 三、全栈式AI系统（FastAPI、路由、安全） ======================
class HybridAugmentor:
    class TextProcessor:
        def __init__(self):
            self.synonyms = {"好": ["优秀","出色"], "坏": ["糟糕","差劲"]}
        def augment(self, text, methods):
            if "synonym" in methods:
                for w, reps in self.synonyms.items():
                    if w in text:
                        text = text.replace(w, np.random.choice(reps))
            return text
    class ImageProcessor:
        def augment(self, image, methods):
            if "mixup" in methods:
                alpha = 0.2
                indices = np.random.permutation(len(image))
                return alpha * image + (1-alpha) * image[indices]
            return image
    def __init__(self):
        self.text = self.TextProcessor()
        self.image = self.ImageProcessor()
    def process(self, data):
        if data.get("modality") == "text":
            data["content"] = self.text.augment(data["content"], ["synonym"])
        elif data.get("modality") == "image":
            data["tensor"] = self.image.augment(data["tensor"], ["mixup"])
        return data

class VectorDatabase:
    def __init__(self):
        self.storage = {}
        self.metadata_store = {}
    def store(self, key, embedding, metadata):
        self.storage[key] = embedding
        self.metadata_store[key] = metadata
    def search(self, query, top_k=5, threshold=0.7):
        results = []
        for key, emb in self.storage.items():
            sim = np.dot(emb, query)
            if sim > threshold:
                results.append((key, sim, self.metadata_store[key]))
        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

class ModelRouter:
    def __init__(self):
        self.models = {
            "cv": nn.Sequential(nn.Conv2d(3,64,3), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(64*16*16,10)),
            "nlp": nn.LSTM(300,128,2,bidirectional=True),
            "multimodal": nn.Transformer(512,8,6)
        }
        self.memory = VectorDatabase()
    def route(self, input_data):
        if input_data.get("dtype") == "image": return self.models["cv"]
        elif "?" in input_data.get("text",""): return self.models["nlp"]
        else:
            res = self.memory.search(input_data["embedding"])
            if res:
                return self.models[res[0][2]["model_type"]]
            return self.models["multimodal"]

class SecurityManager:
    def __init__(self):
        self.cipher = Fernet(Fernet.generate_key())
        self.token_store = {}
    def generate_token(self, user):
        ts = datetime.now().timestamp()
        token = self.cipher.encrypt(f"{user}|{ts}".encode()).decode()
        self.token_store[token] = ts + 3600
        return token
    def validate_token(self, token):
        if token not in self.token_store: return False
        if datetime.now().timestamp() > self.token_store[token]:
            del self.token_store[token]
            return False
        return True
    def encrypt_data(self, data): return self.cipher.encrypt(json.dumps(data).encode())
    def decrypt_data(self, enc): return json.loads(self.cipher.decrypt(enc).decode())

class LLMIntegration:
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()
    def build_prompt(self, query, context):
        return f"基于以下知识：{context}\n回答问题：{query}\n要求：结构清晰，技术细节，代码示例。"
    def query_knowledge(self, query):
        return "示例回答文本"

# FastAPI 应用
app = FastAPI()
security = SecurityManager()
llm_engine = LLMIntegration()

class ModelRequest(BaseModel):
    model: str
    data: dict
    token: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/v3/predict")
async def predict_endpoint(req: ModelRequest):
    if not security.validate_token(req.token):
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        processor = HybridAugmentor()
        processed = processor.process(req.data)
        router = ModelRouter()
        model = router.route(processed)
        inputs = torch.tensor(processed.get("input", [0.0]), dtype=torch.float32)
        with torch.no_grad():
            outputs = model(inputs)
        return {"status": "success", "result": outputs.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v2/ask")
async def ask_endpoint(request: dict):
    context = llm_engine.query_knowledge(request["query"])
    prompt = llm_engine.build_prompt(request["query"], context)
    answer = llm_engine.query_knowledge(prompt)
    return {"question": request["query"], "answer": answer, "sources": context}

# ====================== 四、Bunny模型训练系统（知识蒸馏、自动修复） ======================
class SystemConfigBunny:
    """Bunny系统配置（与之前区分命名）"""
    MODEL_PATHS = {
        "teacher": ["./models/teacher", r"C:\Users\Administrator\Documents\Bunny-v1_0-3B", "BAAI/Bunny-v1_0-3B"],
        "student": ["./models/student", "distilbert-base-uncased"]
    }
    REQUIRED_FILES = {'config.json','pytorch_model.bin','vocab.txt','tokenizer_config.json','special_tokens_map.json'}
    def __init__(self, model_type="teacher"):
        self.model_type = model_type.lower()
        self.base_dir = Path(__file__).parent.absolute()
        self.logger = logging.getLogger(f"Config.{model_type.upper()}")
        try:
            self.model_dir = self._locate_model()
            self._validate_model()
            self._init_workspace()
            self.logger.info(f"Bunny config OK: {self.model_dir}")
        except Exception as e:
            raise RuntimeError(f"Bunny config failed: {e}")
    def _locate_model(self):
        for path in self.MODEL_PATHS[self.model_type]:
            if isinstance(path, str) and (path.startswith("BAAI/") or path.startswith("distilbert")): continue
            cand = Path(path)
            if cand.exists() and self._validate_model_files(cand):
                return cand
        raise FileNotFoundError(f"No valid {self.model_type} model found")
    def _validate_model_files(self, path):
        try:
            existing = set(os.listdir(path))
            missing = self.REQUIRED_FILES - existing
            if missing: return False
            with open(path/"config.json") as f:
                cfg = json.load(f)
            if cfg.get("model_type","").lower() != "bunny": return False
            return True
        except: return False
    def _validate_model(self):
        cfg = AutoConfig.from_pretrained(str(self.model_dir))
        if cfg.model_type.lower() != "bunny":
            raise ValueError("Model type mismatch")
    def _init_workspace(self):
        for d in [self.base_dir/"data", self.base_dir/"logs", self.base_dir/"models/student", self.base_dir/"checkpoints"]:
            d.mkdir(parents=True, exist_ok=True)

class DeviceManagerBunny:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger("DeviceManager")
    def move_to_device(self, data):
        if isinstance(data, torch.Tensor): return data.to(self.device)
        if isinstance(data, dict): return {k: self.move_to_device(v) for k,v in data.items()}
        if isinstance(data, (list, tuple)): return [self.move_to_device(v) for v in data]
        return data

class ModelRepairerBunny:
    @staticmethod
    def repair(model_dir, required_files):
        try:
            from huggingface_hub import snapshot_download
            repo_id = "BAAI/Bunny-v1_0-3B" if "teacher" in str(model_dir) else "distilbert-base-uncased"
            snapshot_download(repo_id=repo_id, local_dir=model_dir, resume_download=True)
            if all((model_dir/f).exists() for f in required_files):
                return model_dir
        except Exception as e:
            logging.error(f"Repair failed: {e}")
        return None

class KnowledgeDistillerBunny:
    def __init__(self, teacher_cfg, student_cfg):
        self.logger = logging.getLogger("Distiller")
        self.device_mgr = DeviceManagerBunny()
        self.teacher, _ = self._load_model(teacher_cfg)
        self.student, _ = self._load_model(student_cfg)
        self.temperature = 2.0
        self.alpha = 0.7
        self.grad_accum = 4
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.device_mgr.device.type == "cuda")
        self.optimizer = optim.AdamW(self.student.parameters(), lr=2e-5, weight_decay=0.01)
    def _load_model(self, cfg):
        model = AutoModelForSequenceClassification.from_pretrained(str(cfg.model_dir),
                                                                  config=AutoConfig.from_pretrained(str(cfg.model_dir)))
        model = model.to(self.device_mgr.device)
        tokenizer = AutoTokenizer.from_pretrained(str(cfg.model_dir))
        return model, tokenizer
    def train(self, train_data, epochs=3):
        for epoch in range(epochs):
            self._train_epoch(train_data, epoch)
    def _train_epoch(self, data, epoch):
        self.teacher.eval()
        self.student.train()
        total_loss = 0.0
        for step, batch in enumerate(data):
            with torch.cuda.amp.autocast(enabled=self.device_mgr.device.type=="cuda"):
                loss = self._distill_step(batch)
                total_loss += loss.item()
        return total_loss / len(data)
    def _distill_step(self, batch):
        batch = self.device_mgr.move_to_device(batch)
        with torch.no_grad():
            teacher_out = self.teacher(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"])
        student_out = self.student(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"])
        soft = nn.KLDivLoss(reduction='batchmean')(
            nn.functional.log_softmax(student_out.logits/self.temperature, dim=1),
            nn.functional.softmax(teacher_out.logits/self.temperature, dim=1)
        ) * (self.temperature**2)
        hard = nn.CrossEntropyLoss()(student_out.logits, batch["labels"])
        loss = self.alpha * soft + (1-self.alpha) * hard
        loss = loss / self.grad_accum
        self.scaler.scale(loss).backward()
        return loss

# ====================== 五、Neuro Factory（PyQt5训练界面、代码生成） ======================
class NeuroConfig:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.base_model = "deepseek-ai/deepseek-llm-1.3b-chat"
            cls._instance.data_dirs = ["./data", "./custom_data"]
            cls._instance.output_dir = Path("./neuro_models")
            cls._instance.cache_dir = Path("./.neuro_cache")
            cls._instance.max_length = 2048
            cls._instance.batch_size = 2
            cls._instance.grad_accum = 4
            cls._instance.epochs = 3
            cls._instance.learning_rate = 2e-5
            cls._instance.lora_r = 8
            cls._instance.lora_alpha = 32
            cls._instance.encrypt_key = Fernet.generate_key().decode()
            cls._instance._prepare_directories()
        return cls._instance
    def _prepare_directories(self):
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        for d in self.data_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

class NeuroDataEngine:
    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        self.tokenizer.pad_token = self.tokenizer.eos_token
    def feed_data(self, files=None):
        all_samples = []
        for data_dir in self.config.data_dirs:
            for path in Path(data_dir).rglob("*"):
                samples = self._process_file(path)
                if samples:
                    all_samples.extend(samples)
        return Dataset.from_dict({
            "instruction": [s["instruction"] for s in all_samples],
            "output": [s["output"] for s in all_samples]
        }) if all_samples else Dataset.from_dict({})
    def _process_file(self, path):
        ext = path.suffix.lower()
        if ext == ".txt":
            return self._process_txt(path)
        elif ext == ".json":
            return self._process_json(path)
        elif ext == ".csv":
            return self._process_csv(path)
        return []
    def _process_txt(self, path):
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            dialog = []
            for line in f:
                line = line.strip()
                if line:
                    dialog.append(line)
                else:
                    if len(dialog) >= 2:
                        samples.append({"instruction": dialog[0].split(":",1)[-1].strip(),
                                        "output": dialog[1].split(":",1)[-1].strip()})
                    dialog = []
        return samples
    def _process_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return [{"instruction": k, "output": v} for k,v in data.items()]
    def _process_csv(self, path):
        df = pd.read_csv(path)
        return [{"instruction": row["question"], "output": str(row["answer"])} for _, row in df.iterrows()]

class ModelVaultNeuro:
    def __init__(self, config):
        self.cipher = Fernet(config.encrypt_key.encode())
    def secure_save(self, model, path):
        state_dict = model.state_dict()
        encrypted = {}
        for name, param in state_dict.items():
            np_param = param.cpu().numpy()
            hashed = hashlib.sha256(np_param.tobytes() + self.cipher._signing_key).digest()
            encrypted[name] = torch.from_numpy(np.frombuffer(hashed[:np_param.nbytes], dtype=np_param.dtype))
        torch.save(encrypted, path)
    def tamper_check(self, path):
        return hashlib.sha256(open(path,'rb').read()).hexdigest() != Path(path+'.hash').read_text()

class NeuroTrainerPyQt(QThread):
    update_log = pyqtSignal(str)
    training_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    def __init__(self, config, dataset):
        super().__init__()
        self.config = config
        self.dataset = dataset
        self.vault = ModelVaultNeuro(config)
    def run(self):
        try:
            model, tokenizer = self._init_model()
            tokenized = self._preprocess(tokenizer)
            args = TrainingArguments(
                output_dir=str(self.config.output_dir),
                per_device_train_batch_size=self._dynamic_batch_size(),
                gradient_accumulation_steps=self.config.grad_accum,
                num_train_epochs=self.config.epochs,
                learning_rate=self.config.learning_rate,
                fp16=torch.cuda.is_available(),
                logging_steps=50,
                save_strategy="epoch"
            )
            trainer = Trainer(model=model, args=args, train_dataset=tokenized,
                              data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False))
            trainer.train()
            self._save_model(model, tokenizer)
            self.training_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    def _init_model(self):
        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                                        bnb_4bit_compute_dtype=torch.bfloat16)
        model = AutoModelForCausalLM.from_pretrained(self.config.base_model, quantization_config=bnb_config,
                                                     device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
        tokenizer.pad_token = tokenizer.eos_token
        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, LoraConfig(r=self.config.lora_r, lora_alpha=self.config.lora_alpha,
                                                 target_modules=["q_proj","v_proj"], task_type="CAUSAL_LM"))
        return model, tokenizer
    def _dynamic_batch_size(self):
        if torch.cuda.is_available():
            free = torch.cuda.mem_get_info()[0] / (1024**3)
            return 4 if free > 20 else 2 if free > 10 else 1
        return 1
    def _preprocess(self, tokenizer):
        return self.dataset.map(
            lambda x: tokenizer([f"Instruction: {i}\nOutput: {o}" for i,o in zip(x["instruction"], x["output"])],
                                truncation=True, max_length=self.config.max_length, padding="max_length"),
            batched=True, remove_columns=["instruction","output"]
        )
    def _save_model(self, model, tokenizer):
        out_dir = self.config.output_dir / datetime.now().strftime("%Y%m%d_%H%M")
        out_dir.mkdir()
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        self.vault.secure_save(model, out_dir/"model_encrypted.bin")
        (out_dir/"model.hash").write_text(self.vault._ModelVaultNeuro__compute_hash(out_dir/"model_encrypted.bin"))
        self.update_log.emit(f"模型已保存至 {out_dir}")

class CodeGenerator:
    TEMPLATES = {
        "web_app": {
            "main.py": "from flask import Flask\napp=Flask(__name__)\n@app.route('/')\ndef index(): return 'Hello'\nif __name__=='__main__': app.run()",
            "requirements.txt": "flask>=2.0.0"
        },
        "cli_tool": {
            "main.py": "import click\n@click.command()\ndef cli(): click.echo('Hello')\nif __name__=='__main__': cli()",
            "requirements.txt": "click>=8.0.0"
        }
    }
    def generate(self, project_type, features, output_dir):
        out = Path(output_dir)
        out.mkdir(exist_ok=True)
        for fname, content in self.TEMPLATES[project_type].items():
            (out/fname).write_text(content)
        return str(out)

class NeuroGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = NeuroConfig()
        self.data_engine = NeuroDataEngine(self.config)
        self.code_gen = CodeGenerator()
        self.trainer = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Neuro Factory Ultimate")
        self.setGeometry(100,100,1200,800)
        tabs = QTabWidget()
        # 训练选项卡
        train_tab = QWidget()
        train_layout = QVBoxLayout()
        self.btn_load = QPushButton("加载数据")
        self.btn_train = QPushButton("开始训练")
        self.log_display = QTextEdit()
        train_layout.addWidget(self.btn_load)
        train_layout.addWidget(self.btn_train)
        train_layout.addWidget(QLabel("训练日志"))
        train_layout.addWidget(self.log_display)
        train_tab.setLayout(train_layout)
        # 代码生成选项卡
        code_tab = QWidget()
        code_layout = QVBoxLayout()
        self.project_type = QComboBox()
        self.project_type.addItems(["web_app","cli_tool"])
        self.features_input = QLineEdit("user,admin")
        self.btn_gen_code = QPushButton("生成代码")
        code_layout.addWidget(QLabel("项目类型"))
        code_layout.addWidget(self.project_type)
        code_layout.addWidget(QLabel("功能列表"))
        code_layout.addWidget(self.features_input)
        code_layout.addWidget(self.btn_gen_code)
        code_tab.setLayout(code_layout)
        # 安全选项卡
        security_tab = QWidget()
        security_layout = QVBoxLayout()
        self.btn_encrypt = QPushButton("加密文件")
        self.btn_decrypt = QPushButton("解密文件")
        security_layout.addWidget(self.btn_encrypt)
        security_layout.addWidget(self.btn_decrypt)
        security_tab.setLayout(security_layout)
        tabs.addTab(train_tab, "模型训练")
        tabs.addTab(code_tab, "代码生成")
        tabs.addTab(security_tab, "安全中心")
        self.setCentralWidget(tabs)
        self.btn_load.clicked.connect(self.load_data)
        self.btn_train.clicked.connect(self.start_training)
        self.btn_gen_code.clicked.connect(self.generate_code)
        self.btn_encrypt.clicked.connect(lambda: self.security_operation("encrypt"))
        self.btn_decrypt.clicked.connect(lambda: self.security_operation("decrypt"))
    def load_data(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择数据文件", "", "*.txt *.json *.csv")
        if files:
            try:
                self.data_engine.feed_data(files)
                self.log_display.append(f"[{datetime.now()}] 加载 {len(files)} 个文件")
            except Exception as e:
                self.log_display.append(f"[{datetime.now()}] 加载失败: {e}")
    def start_training(self):
        dataset = self.data_engine.feed_data()
        if len(dataset)==0:
            QMessageBox.critical(self, "错误", "无训练数据")
            return
        self.trainer = NeuroTrainerPyQt(self.config, dataset)
        self.trainer.update_log.connect(self.log_display.append)
        self.trainer.training_finished.connect(lambda: QMessageBox.information(self,"完成","训练完成"))
        self.trainer.error_occurred.connect(lambda msg: QMessageBox.critical(self,"错误",msg))
        self.trainer.start()
    def generate_code(self):
        project_type = self.project_type.currentText()
        features = [f.strip() for f in self.features_input.text().split(",")]
        out_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if out_dir and features:
            try:
                path = self.code_gen.generate(project_type, features, out_dir)
                self.log_display.append(f"[{datetime.now()}] 代码生成至 {path}")
            except Exception as e:
                self.log_display.append(f"[{datetime.now()}] 生成失败: {e}")
    def security_operation(self, op_type):
        file, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if not file: return
        try:
            vault = ModelVaultNeuro(self.config)
            if op_type == "encrypt":
                vault.secure_save(torch.load(file), file+".enc")
            else:
                dec = vault.cipher.decrypt(Path(file).read_bytes())
                Path(file.replace(".enc","")).write_bytes(dec)
            self.log_display.append(f"[{datetime.now()}] {op_type} 操作完成")
        except Exception as e:
            self.log_display.append(f"[{datetime.now()}] 安全操作失败: {e}")

# ====================== 六、AI Factory（监控、数据监控） ======================
class GlobalConfigAIFactory:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.model_path = "deepseek-ai/deepseek-llm-1.3b-chat"
            cls._instance.data_dirs = ["./data", "./custom_data"]
            cls._instance.output_dir = Path("./neuro_models")
            cls._instance.cache_dir = Path("./.neuro_cache")
            cls._instance.max_length = 2048
            cls._instance.batch_size = 2
            cls._instance.grad_accum = 4
            cls._instance.epochs = 3
            cls._instance.learning_rate = 2e-5
            cls._instance.lora_r = 8
            cls._instance.lora_alpha = 32
            cls._instance.encryption_key = Fernet.generate_key().decode()
            cls._instance.quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                                                            bnb_4bit_compute_dtype=torch.bfloat16)
            cls._instance._prepare_directories()
        return cls._instance
    def _prepare_directories(self):
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        for d in self.data_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

class DataWatcher:
    def __init__(self, callback):
        self.observer = Observer()
        self.event_handler = DataHandler(callback)
    def start(self, path):
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()

class DataHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.txt','.json','.csv')):
            self.callback(Path(event.src_path))

class MultiModalDataEngineAIFactory:
    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token
    def load_data(self, files=None):
        all_samples = []
        for data_dir in self.config.data_dirs:
            for path in Path(data_dir).rglob("*"):
                samples = self._process_file(path)
                if samples:
                    all_samples.extend(samples)
        return Dataset.from_dict({
            "instruction": [s["instruction"] for s in all_samples],
            "output": [s["output"] for s in all_samples]
        }) if all_samples else Dataset.from_dict({})
    def _process_file(self, path):
        ext = path.suffix.lower()
        if ext == ".txt":
            return self._process_txt(path)
        elif ext == ".json":
            return self._process_json(path)
        elif ext == ".csv":
            return self._process_csv(path)
        return []
    def _process_txt(self, path):
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            dialog = []
            for line in f:
                line = line.strip()
                if line:
                    dialog.append(line)
                else:
                    if len(dialog) >= 2:
                        samples.append({"instruction": dialog[0].split(":",1)[-1].strip(),
                                        "output": dialog[1].split(":",1)[-1].strip()})
                    dialog = []
        return samples
    def _process_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return [{"instruction": k, "output": v} for k,v in data.items()]
    def _process_csv(self, path):
        df = pd.read_csv(path)
        return [{"instruction": row["question"], "output": str(row["answer"])} for _, row in df.iterrows()]

class ModelVaultAIFactory:
    def __init__(self, config):
        self.cipher = Fernet(config.encryption_key.encode())
    def encrypt_model(self, model_dir):
        for f in model_dir.glob("*"):
            if f.suffix in (".bin", ".pth"):
                f.write_bytes(self.cipher.encrypt(f.read_bytes()))
    def decrypt_model(self, model_dir):
        for f in model_dir.glob("*"):
            if f.suffix in (".bin", ".pth"):
                f.write_bytes(self.cipher.decrypt(f.read_bytes()))
    def verify_model(self, model_dir):
        try:
            for f in model_dir.glob("*"):
                if f.suffix == ".hash": continue
                if hashlib.sha256(f.read_bytes()).hexdigest() != (model_dir / f"{f.name}.hash").read_text():
                    return False
            return True
        except: return False

class NeuroTrainerAIFactory(QThread):
    progress_updated = pyqtSignal(int, float)
    training_finished = pyqtSignal()
    log_message = pyqtSignal(str)
    def __init__(self, dataset):
        super().__init__()
        self.config = GlobalConfigAIFactory()
        self.dataset = dataset
    def run(self):
        try:
            self.log_message.emit("初始化模型...")
            model, tokenizer = self._init_model()
            tokenized = self.dataset.map(lambda x: self._tokenize(x, tokenizer),
                                         batched=True, remove_columns=["instruction","output"])
            args = TrainingArguments(
                output_dir=str(self.config.output_dir),
                per_device_train_batch_size=self._dynamic_batch_size(),
                gradient_accumulation_steps=self.config.grad_accum,
                num_train_epochs=self.config.epochs,
                learning_rate=self.config.learning_rate,
                fp16=torch.cuda.is_available(),
                logging_steps=50,
                save_strategy="epoch"
            )
            trainer = Trainer(model=model, args=args, train_dataset=tokenized,
                              data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False))
            trainer.add_callback(TrainingCallback(self.progress_updated))
            self.log_message.emit("开始训练...")
            trainer.train()
            self._save_model(model, tokenizer)
            self.training_finished.emit()
        except Exception as e:
            self.log_message.emit(f"训练失败: {e}")
    def _init_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.config.model_path,
                                                     quantization_config=self.config.quant_config,
                                                     device_map="auto")
        model = prepare_model_for_kbit_training(model)
        peft_config = LoraConfig(r=self.config.lora_r, lora_alpha=self.config.lora_alpha,
                                 target_modules=["q_proj","v_proj"], task_type="CAUSAL_LM")
        return get_peft_model(model, peft_config), AutoTokenizer.from_pretrained(self.config.model_path)
    def _dynamic_batch_size(self):
        if torch.cuda.is_available():
            free = torch.cuda.mem_get_info()[0] / (1024**3)
            return 4 if free > 20 else 2 if free > 10 else 1
        return 1
    def _tokenize(self, examples, tokenizer):
        texts = [f"Instruction: {i}\nOutput: {o}" for i,o in zip(examples["instruction"], examples["output"])]
        return tokenizer(texts, truncation=True, max_length=self.config.max_length, padding="max_length")
    def _save_model(self, model, tokenizer):
        out_dir = self.config.output_dir / datetime.now().strftime("%Y%m%d_%H%M")
        out_dir.mkdir()
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        vault = ModelVaultAIFactory(self.config)
        vault.encrypt_model(out_dir)
        for f in out_dir.glob("*"):
            if f.suffix in (".bin", ".pth"):
                (out_dir / f"{f.name}.hash").write_text(hashlib.sha256(f.read_bytes()).hexdigest())
        self.log_message.emit(f"模型保存至 {out_dir}")

class TrainingCallback:
    def __init__(self, signal):
        self.signal = signal
    def on_log(self, args, state, control, logs=None, **kwargs):
        if "loss" in logs:
            self.signal.emit(state.epoch, logs["loss"])

class AIFactoryGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = GlobalConfigAIFactory()
        self.data_engine = MultiModalDataEngineAIFactory(self.config)
        self.vault = ModelVaultAIFactory(self.config)
        self.current_model = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("AI Factory Pro v6.0")
        self.setGeometry(100,100,1280,800)
        tabs = QTabWidget()
        # 数据管理
        data_tab = QWidget()
        layout = QVBoxLayout()
        self.data_dir_input = QLineEdit(str(self.config.data_dirs[0]))
        btn_browse = QPushButton("浏览")
        btn_load = QPushButton("加载数据")
        layout.addWidget(QLabel("数据目录:"))
        layout.addWidget(self.data_dir_input)
        layout.addWidget(btn_browse)
        layout.addWidget(btn_load)
        self.data_preview = QTextEdit()
        layout.addWidget(self.data_preview)
        data_tab.setLayout(layout)
        btn_load.clicked.connect(self.load_data)
        # 训练控制
        train_tab = QWidget()
        layout2 = QVBoxLayout()
        self.progress_bar = QProgressBar()
        btn_train = QPushButton("开始训练")
        self.train_log = QTextEdit()
        layout2.addWidget(self.progress_bar)
        layout2.addWidget(btn_train)
        layout2.addWidget(self.train_log)
        train_tab.setLayout(layout2)
        btn_train.clicked.connect(self.start_training)
        # 推理测试
        infer_tab = QWidget()
        layout3 = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("输入指令...")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        btn_gen = QPushButton("生成")
        layout3.addWidget(self.input_text)
        layout3.addWidget(btn_gen)
        layout3.addWidget(self.output_text)
        infer_tab.setLayout(layout3)
        btn_gen.clicked.connect(self.generate_response)
        tabs.addTab(data_tab, "数据管理")
        tabs.addTab(train_tab, "训练控制")
        tabs.addTab(infer_tab, "推理测试")
        self.setCentralWidget(tabs)
    def load_data(self):
        self.data_engine.load_data()
        self.data_preview.append("数据加载完成")
    def start_training(self):
        dataset = self.data_engine.load_data()
        if len(dataset)==0:
            QMessageBox.critical(self, "错误", "无数据")
            return
        self.trainer = NeuroTrainerAIFactory(dataset)
        self.trainer.log_message.connect(self.train_log.append)
        self.trainer.progress_updated.connect(lambda e,l: self.progress_bar.setValue(int(e/self.config.epochs*100)))
        self.trainer.start()
    def generate_response(self):
        self.output_text.append("生成功能示例，需加载模型。")

# ====================== 七、企业级智能文件管理（Flask、SQLAlchemy） ======================
# 此模块未完整提供，此处仅做占位说明，避免缺失。
class EnterpriseFileManager:
    """企业级文件管理模块（占位）"""
    def __init__(self):
        logger.info("文件管理模块已预留，需补充完整实现。")

# ====================== 主入口 ======================
def main():
    """统一入口，可选择启动哪个子系统"""
    import sys
    # 默认启动 PyQt5 NeuroGUI
    app = QApplication(sys.argv)
    win = NeuroGUI()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()