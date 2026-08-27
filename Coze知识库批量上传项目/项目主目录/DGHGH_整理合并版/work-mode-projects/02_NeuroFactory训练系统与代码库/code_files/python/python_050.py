# ========== Bunny 模型训练系统 ==========
import os
import json
import logging
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import (
    AutoConfig, AutoModelForSequenceClassification, AutoTokenizer,
    BitsAndBytesConfig, get_peft_model, LoraConfig, prepare_model_for_kbit_training
)
from peft import LoraConfig, get_peft_model

class SystemConfigBunny:
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