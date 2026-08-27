# ========== AI Factory（监控与训练） ==========
import os
import json
import time
from pathlib import Path
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import QThread, pyqtSignal
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
    DataCollatorForLanguageModeling, BitsAndBytesConfig, prepare_model_for_kbit_training
)
from peft import LoraConfig, get_peft_model
from datasets import Dataset
import pandas as pd
from cryptography.fernet import Fernet
import hashlib
from datetime import datetime

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

class DataHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.txt','.json','.csv')):
            self.callback(Path(event.src_path))

class DataWatcher:
    def __init__(self, callback):
        self.observer = Observer()
        self.event_handler = DataHandler(callback)
    def start(self, path):
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()

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
        if ext == ".txt": return self._process_txt(path)
        elif ext == ".json": return self._process_json(path)
        elif ext == ".csv": return self._process_csv(path)
        return []
    def _process_txt(self, path):
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            dialog = []
            for line in f:
                line = line.strip()
                if line: dialog.append(line)
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