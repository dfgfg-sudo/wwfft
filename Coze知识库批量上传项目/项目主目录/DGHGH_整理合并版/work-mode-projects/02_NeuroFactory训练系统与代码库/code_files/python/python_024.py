#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NeuroFactory Pro - 全功能企业级AI开发平台
最终整合版 (基于 5.0/4.0/6.0/7.0 合并优化)
"""
import os
import json
import logging
import torch
import faiss
import gradio as gr
import numpy as np
import pandas as pd
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from cryptography.fernet import Fernet
from datasets import Dataset, load_from_disk, concatenate_datasets
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    EarlyStoppingCallback
)
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

# ====================== 量子计算核心系统 ======================
class QuantumProcessor:
    """量子计算处理单元（来自 v5.0/v7.0）"""
    def __init__(self):
        self.quantum_state = None
        self.gate_history = []
        self.classical_buffer = np.zeros(1024, dtype=np.complex128)

    def apply_gate(self, gate_matrix: np.ndarray):
        if self.quantum_state is None:
            self.quantum_state = np.eye(2, dtype=np.complex128)
        self.quantum_state = np.kron(self.quantum_state, gate_matrix)
        self.gate_history.append(gate_matrix)

    def quantum_embedding(self, data: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(data)
        return data / norm if norm != 0 else data

    def hybrid_inference(self, input_tensor: torch.Tensor) -> torch.Tensor:
        quantum_data = self.quantum_embedding(input_tensor.numpy())
        return torch.from_numpy(quantum_data * 0.8 + input_tensor.numpy() * 0.2)

# ====================== 全局配置管理（单例） ======================
class NeuroConfig:
    """统一配置管理中心（来自 v6.0/v7.0）"""
    _instance = None

    def __new__(cls, project_root: str = None):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            if project_root:
                cls._instance._initialize(Path(project_root))
            else:
                cls._instance._default_init()
        return cls._instance

    def _default_init(self):
        self.root = Path(".")
        self.model_dir = self.root / "pretrained"
        self.data_dirs = [self.root / "data"]
        self.output_dir = self.root / "output"
        self.cache_dir = self.root / "cache"
        self.encrypt_key = Fernet.generate_key().decode()
        self._init_directories()
        self._init_logging()

    def _initialize(self, root_path: Path):
        self.root = root_path
        config_file = root_path / "neuro_config.yaml"
        if config_file.exists():
            import yaml
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
                self.__dict__.update(config_data)
        self._init_directories()
        self._init_logging()

    def _init_directories(self):
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.cache_dir.mkdir(exist_ok=True)
        for path in self.data_dirs:
            path.mkdir(exist_ok=True, parents=True)

    def _init_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.output_dir / "neuro_factory.log"),
                logging.StreamHandler()
            ]
        )

# ====================== 多模态数据引擎 ======================
class DataEngine:
    """智能数据处理系统（来自 v6.0）"""
    def __init__(self, config: NeuroConfig):
        self.cfg = config
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.cfg.model_dir))

    def build_dataset(self, refresh=False) -> Dataset:
        cache_path = self.cfg.cache_dir / "processed_data"
        if not refresh and cache_path.exists():
            return load_from_disk(cache_path)
        return self._process_data(cache_path)

    def _process_data(self, cache_path: Path) -> Dataset:
        futures = []
        for data_dir in self.cfg.data_dirs:
            for file in data_dir.glob("**/*"):
                if file.suffix in (".txt", ".json", ".csv"):
                    futures.append(self.executor.submit(self._parse_file, file))
        samples = []
        for future in futures:
            samples.extend(future.result())
        dataset = Dataset.from_dict({
            "instruction": [s["instruction"] for s in samples],
            "output": [s["output"] for s in samples]
        })
        dataset.save_to_disk(cache_path)
        return dataset

    def _parse_file(self, file: Path) -> List[Dict]:
        parsers = {
            ".txt": self._parse_dialog,
            ".json": self._parse_knowledge,
            ".csv": self._parse_table
        }
        return parsers.get(file.suffix, lambda _: [])(file)

    def _parse_dialog(self, file: Path) -> List[Dict]:
        samples = []
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().replace('\r\n', '\n')
            for dialog in content.split("\n\n"):
                lines = [line.strip() for line in dialog.split("\n") if line.strip()]
                for i in range(0, len(lines)-1, 2):
                    context = "\n".join(lines[max(0,i-4):i+1])
                    samples.append({
                        "instruction": context,
                        "output": lines[i+1]
                    })
        return samples

    def _parse_knowledge(self, file: Path) -> List[Dict]:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [{"instruction": k, "output": v} for k, v in data.items()]

    def _parse_table(self, file: Path) -> List[Dict]:
        try:
            df = pd.read_csv(file)
            return [{
                "instruction": row["question"],
                "output": str(row["answer"])
            } for _, row in df.iterrows() if "question" in df.columns and "answer" in df.columns]
        except Exception as e:
            logging.error(f"CSV解析失败: {file.name} - {str(e)}")
            return []

    def tokenize(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            lambda x: self.tokenizer(
                f"Instruction: {x['instruction']}\nOutput: {x['output']}",
                max_length=self.cfg.max_seq_len,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            ),
            batched=True,
            remove_columns=["instruction", "output"]
        )

# ====================== 量子增强训练系统 ======================
class QuantumTrainer(QuantumProcessor):
    """量子增强训练引擎（来自 v5.0/v7.0）"""
    def __init__(self, config: NeuroConfig):
        super().__init__()
        self.cfg = config
        self.model, self.tokenizer = self._init_model()
        self.loss_history = []

    def _init_model(self):
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_dir,
            quantization_config=quant_config,
            device_map="auto"
        )
        model = prepare_model_for_kbit_training(model)
        peft_config = LoraConfig(
            r=self.cfg.lora_rank,
            lora_alpha=self.cfg.lora_alpha,
            target_modules=self.cfg.target_modules,
            task_type="CAUSAL_LM"
        )
        return get_peft_model(model, peft_config), \
               AutoTokenizer.from_pretrained(self.cfg.model_dir)

    def train(self, dataset: Dataset):
        tokenized_data = dataset.map(
            self._enhance_data,
            batched=True,
            batch_size=self._auto_batch_size()
        )
        training_args = TrainingArguments(
            output_dir=str(self.cfg.output_dir),
            per_device_train_batch_size=self._auto_batch_size(),
            gradient_accumulation_steps=self.cfg.grad_accum,
            learning_rate=self.cfg.learning_rate,
            num_train_epochs=self.cfg.epochs,
            fp16=True,
            logging_steps=20,
            save_strategy="epoch",
            report_to=["tensorboard"]
        )
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_data,
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False)
        )
        trainer.train()
        self._save_model()

    def _enhance_data(self, examples):
        # 简化的量子增强：添加前缀标记
        enhanced = [f"QuantumEnhanced: {text}" for text in examples["instruction"]]
        return self.tokenizer(enhanced, padding="max_length", truncation=True)

    def _auto_batch_size(self) -> int:
        free_mem = torch.cuda.mem_get_info()[0] // (1024 ** 3)
        return min(4, max(1, free_mem // 2))

    def _save_model(self):
        self.model.save_pretrained(self.cfg.output_dir / "lora_adapters")
        logging.info(f"模型已保存至: {self.cfg.output_dir}")

# ====================== 安全管理系统 ======================
class SecurityManager:
    """模型安全中心（来自 v5.0/v6.0）"""
    def __init__(self, config: NeuroConfig):
        self.cfg = config
        self.cipher = Fernet(config.encrypt_key.encode())
        self.hashes = {}

    def encrypt_model(self, model_dir: Path):
        for file in model_dir.glob("**/*"):
            if file.is_file():
                encrypted = self.cipher.encrypt(file.read_bytes())
                file.write_bytes(encrypted)
                self.hashes[file.name] = hashlib.sha3_256(encrypted).hexdigest()

    def decrypt_model(self, model_dir: Path):
        for file in model_dir.glob("**/*"):
            decrypted = self.cipher.decrypt(file.read_bytes())
            file.write_bytes(decrypted)

    def validate(self, model_dir: Path) -> bool:
        for file in model_dir.glob("**/*"):
            current_hash = hashlib.sha3_256(file.read_bytes()).hexdigest()
            if self.hashes.get(file.name) != current_hash:
                return False
        return True

# ====================== 企业级交互界面 ======================
class NeuroDashboard:
    """统一管理系统界面（来自 v5.0/v6.0）"""
    def __init__(self):
        self.cfg = NeuroConfig()
        self.data_engine = DataEngine(self.cfg)
        self.trainer = None

    def launch(self):
        with gr.Blocks(title="Neuro Factory Pro", theme=gr.themes.Soft()) as ui:
            gr.Markdown("# 🧠 智能AI训练平台 - 企业版")

            with gr.Row():
                project_input = gr.Textbox(label="项目路径", placeholder="输入或拖入项目文件夹...")
                load_btn = gr.Button("加载项目", variant="primary")

            with gr.Tab("模型训练"):
                with gr.Row():
                    data_btn = gr.Button("加载数据", variant="secondary")
                    train_btn = gr.Button("开始训练", variant="primary")
                with gr.Accordion("高级设置", open=False):
                    lora_r = gr.Slider(8, 64, 8, step=8, label="LoRA秩")
                    lora_alpha = gr.Slider(16, 128, 32, step=16, label="LoRA Alpha")
                loss_plot = gr.LinePlot(label="训练损失曲线")

            with gr.Tab("安全管理"):
                with gr.Row():
                    encrypt_btn = gr.Button("加密模型")
                    decrypt_btn = gr.Button("解密模型")
                status = gr.Textbox(label="操作状态")

            logs = gr.Textbox(label="运行日志", lines=8)

            load_btn.click(self._load_project, [project_input], [logs])
            data_btn.click(self._load_data, outputs=[logs])
            train_btn.click(self._start_train, [lora_r, lora_alpha], [logs, loss_plot])
            encrypt_btn.click(self._encrypt_model, outputs=[status])
            decrypt_btn.click(self._decrypt_model, outputs=[status])

        ui.launch(server_port=7860)

    def _load_project(self, path: str) -> str:
        try:
            self.cfg = NeuroConfig(path)
            self.data_engine = DataEngine(self.cfg)
            return f"✅ 项目加载成功: {path}"
        except Exception as e:
            return f"❌ 加载失败: {str(e)}"

    def _load_data(self) -> str:
        try:
            self.dataset = self.data_engine.build_dataset()
            return f"✅ 已加载 {len(self.dataset)} 条训练数据"
        except Exception as e:
            return f"❌ 数据加载失败: {str(e)}"

    def _start_train(self, lora_r: int, lora_alpha: int) -> tuple:
        try:
            self.cfg.lora_rank = lora_r
            self.cfg.lora_alpha = lora_alpha
            self.trainer = QuantumTrainer(self.cfg)
            self.trainer.train(self.dataset)
            return (
                "🎉 训练完成！模型已保存至/output目录",
                gr.LinePlot.update(
                    value={"x": list(range(len(self.trainer.loss_history))),
                           "y": self.trainer.loss_history}
                )
            )
        except Exception as e:
            return f"❌ 训练失败: {str(e)}", gr.LinePlot.update()

    def _encrypt_model(self) -> str:
        try:
            model_dir = self.cfg.output_dir / "lora_adapters"
            self.security = SecurityManager(self.cfg)
            self.security.encrypt_model(model_dir)
            return "🔒 模型加密完成"
        except Exception as e:
            return f"❌ 加密失败: {str(e)}"

    def _decrypt_model(self) -> str:
        try:
            model_dir = self.cfg.output_dir / "lora_adapters"
            self.security = SecurityManager(self.cfg)
            self.security.decrypt_model(model_dir)
            return "🔓 模型解密完成"
        except Exception as e:
            return f"❌ 解密失败: {str(e)}"

# ====================== 主程序入口 ======================
if __name__ == "__main__":
    assert torch.cuda.is_available(), "需要NVIDIA GPU支持"
    NeuroDashboard().launch()