# ========== Transformer 本地数据智能投喂 ==========
import os
import json
import csv
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, T5ForConditionalGeneration,
    AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
)
from torch.utils.data import Dataset as TorchDataset

SYSTEM_CONFIG = {
    "LOCAL_MODEL_PATH": r"./neuro_data",
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
        return image_path

class AudioAugmentor:
    def augment(self, audio_path: str) -> str:
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
        print(f"训练完成，模型保存至: {self.training_args.output_dir}")

class DataEventHandler(FileSystemEventHandler):
    def __init__(self, processor: DataProcessor, trainer: TransformerTrainer):
        self.processor = processor
        self.trainer = trainer
        self.data_count = 0
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            data_type = self._infer_data_type(file_path)
            if data_type in SYSTEM_CONFIG["SUPPORTED_MODES"]:
                print(f"检测到新数据: {file_path}, 类型: {data_type}")
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