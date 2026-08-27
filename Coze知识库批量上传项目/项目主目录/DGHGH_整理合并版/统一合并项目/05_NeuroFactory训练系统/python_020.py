# -*- coding: utf-8 -*-
"""
全功能AI训练系统 v6.0
最终大融合整合版 - 支持多模态训练与生产部署
包含：文本/图像/视频处理、并行加载、特征工程、混合精度训练、API部署
"""

import os
import json
import torch
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    ViTFeatureExtractor
)
from datasets import Dataset
import pandas as pd
import cv2
import tempfile
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from threading import Thread
from datetime import datetime

# ==================== 系统配置 ====================
class SystemConfig:
    """全局配置管理器"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.device = self._detect_device()
        self._optimize_hardware()
        
    def _setup_logging(self) -> logging.Logger:
        log_file = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger(__name__)
        logger.info(f"初始化系统配置 | 设备类型: {self.device.upper()}")
        return logger
    
    def _detect_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    def _optimize_hardware(self):
        if self.device == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_num_threads(min(4, os.cpu_count() or 1))

# ==================== 核心训练系统 ====================
class AITrainingSystem:
    VERSION = "6.0.0"
    
    def __init__(self, config_path: str = "config.json"):
        self.cfg = SystemConfig()
        self.logger = self.cfg.logger
        self.config = self._load_config(config_path)
        self._validate_config()
        
        self.tokenizer = self._init_tokenizer()
        self.model = self._init_model()
        
        self.data_manager = DataManager(self.config, self.logger)
        self.feature_engine = FeatureEngine(self.config, self.logger)
        self.trainer = ModelTrainer(self.config, self.logger)
        self.deployer = ModelDeployer(self.logger)

        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                user_config = json.load(f)
            defaults = {
                "fp16": self.cfg.device != "cpu",
                "gradient_checkpointing": True,
                "auto_deploy": False,
                "frame_interval": 5,
                "max_length": 512,
                "batch_size": 4 if self.cfg.device != "cpu" else 2,
                "epochs": 3,
                "learning_rate": 5e-5,
                "num_workers": min(4, os.cpu_count() or 1),
                "enable_image": False,
                "enable_video": False,
                "image_model_path": "google/vit-base-patch16-224",
                "save_total_limit": 3,
                "data_dir": "./data",
                "output_dir": "./output",
                "model_path": "gpt2"
            }
            return {**defaults, **user_config}
        except Exception as e:
            self.logger.error(f"配置加载失败: {str(e)}")
            raise

    def _validate_config(self):
        required_keys = ["model_path", "data_dir", "output_dir"]
        missing = [k for k in required_keys if k not in self.config]
        if missing:
            raise ValueError(f"缺少必需配置项: {missing}")

    def _init_tokenizer(self) -> AutoTokenizer:
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                self.config["model_path"],
                padding_side="right",
                truncation_side="right"
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            return tokenizer
        except Exception as e:
            self.logger.error(f"Tokenizer初始化失败: {str(e)}")
            raise

    def _init_model(self) -> AutoModelForCausalLM:
        try:
            torch_dtype = torch.float16 if self.config["fp16"] else torch.float32
            model = AutoModelForCausalLM.from_pretrained(
                self.config["model_path"],
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                device_map="auto" if self.cfg.device != "cpu" else None
            )
            if self.config["gradient_checkpointing"]:
                model.gradient_checkpointing_enable()
            return model.to(self.cfg.device)
        except Exception as e:
            self.logger.error(f"模型初始化失败: {str(e)}")
            raise

    def run_pipeline(self) -> Dict:
        try:
            self.logger.info(f"🚀 启动AI训练系统 v{self.VERSION}")
            dataset = self._stage("数据准备", self.data_manager.load_data)
            processed_data = self._stage("特征处理", self.feature_engine.process, dataset)
            self._stage("模型训练", self.trainer.train, self.model, processed_data)
            if self.config["auto_deploy"]:
                self._stage("API部署", self._launch_deployment)
            return {
                "status": "success",
                "model_path": self.config["output_dir"],
                "log_file": self.logger.handlers[0].baseFilename,
                "config": self.config
            }
        except Exception as e:
            self.logger.error(f"💥 流程执行失败: {str(e)}", exc_info=True)
            raise

    def _stage(self, name: str, func: callable, *args):
        self.logger.info(f"🔛 开始阶段：{name}")
        start = datetime.now()
        result = func(*args)
        elapsed = (datetime.now() - start).total_seconds()
        self.logger.info(f"✅ 完成阶段：{name} | 耗时: {elapsed:.2f}秒")
        return result

    def _launch_deployment(self):
        Thread(target=self.deployer.deploy, args=(self.model, self.tokenizer, self.config["output_dir"]), daemon=True).start()

# ==================== 数据管理（合并扩展名） ====================
class DataManager:
    SUPPORTED_TYPES = {
        'text': ['.txt', '.csv', '.json'],
        'image': ['.jpg', '.jpeg', '.png', '.bmp'],
        'video': ['.mp4', '.avi', '.mov', '.mkv']
    }
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self._init_processors()

    def _init_processors(self):
        self.processors = {}
        for ext in self.SUPPORTED_TYPES['text']:
            if ext == '.csv':
                self.processors[ext] = self._process_csv
            elif ext == '.json':
                self.processors[ext] = self._process_json
            else:
                self.processors[ext] = self._process_text
        if self.config["enable_image"]:
            for ext in self.SUPPORTED_TYPES['image']:
                self.processors[ext] = self._process_image
        if self.config["enable_video"]:
            for ext in self.SUPPORTED_TYPES['video']:
                self.processors[ext] = self._process_video

    def load_data(self) -> Dataset:
        try:
            files = list(self._discover_files())
            if not files:
                raise ValueError(f"未找到数据文件: {self.config['data_dir']}")
            self.logger.info(f"📂 发现 {len(files)} 个数据文件")
            raw_data = self._parallel_process(files)
            if not raw_data:
                raise ValueError("未加载到有效数据")
            return self._create_dataset(raw_data)
        except Exception as e:
            self.logger.error(f"❌ 数据加载失败: {str(e)}")
            raise

    def _discover_files(self):
        data_dir = Path(self.config["data_dir"])
        if not data_dir.exists():
            raise FileNotFoundError(f"数据目录不存在: {data_dir}")
        for ext in self.processors:
            for file in data_dir.rglob(f"*{ext}"):
                if file.is_file():
                    yield file

    def _parallel_process(self, files: List[Path]) -> List[Dict]:
        with ThreadPoolExecutor(max_workers=self.config["num_workers"]) as executor:
            futures = [executor.submit(self._process_file, f) for f in files]
            results = []
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        results.extend(result)
                except Exception as e:
                    self.logger.warning(f"⚠️ 文件处理异常: {str(e)}")
            return results

    def _process_file(self, file: Path) -> List[Dict]:
        processor = self.processors.get(file.suffix.lower())
        return processor(file) if processor else []

    def _process_text(self, file: Path) -> List[Dict]:
        content = file.read_text(encoding='utf-8')
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return [{"text": line, "type": "text", "source": str(file)} for line in lines]

    def _process_csv(self, file: Path) -> List[Dict]:
        df = pd.read_csv(file)
        if 'text' not in df.columns:
            return []
        return [{"text": str(row['text']), "type": "text", "source": str(file)} for _, row in df.iterrows()]

    def _process_json(self, file: Path) -> List[Dict]:
        data = json.loads(file.read_text(encoding='utf-8'))
        data = data if isinstance(data, list) else [data]
        return [{"text": json.dumps(item, ensure_ascii=False), "type": "text", "source": str(file)} for item in data]

    def _process_image(self, file: Path) -> List[Dict]:
        img = cv2.imread(str(file))
        if img is None:
            return []
        return [{"path": str(file), "type": "image", "source": str(file)}]

    def _process_video(self, file: Path) -> List[Dict]:
        cap = cv2.VideoCapture(str(file))
        if not cap.isOpened():
            return []
        cap.release()
        return [{"path": str(file), "type": "video", "source": str(file)}]

    def _create_dataset(self, data: List) -> Dataset:
        return Dataset.from_dict({
            "text": [d.get("text", d.get("path", "")) for d in data],
            "type": [d.get("type", "text") for d in data],
            "source": [d.get("source", "") for d in data]
        })

# ==================== 特征工程 ====================
class FeatureEngine:
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self._init_processors()

    def _init_processors(self):
        self.text_processor = TextProcessor(self.config["model_path"])
        if self.config["enable_image"] or self.config["enable_video"]:
            self.image_processor = ImageProcessor(self.config.get("image_model_path"), self.logger)
        else:
            self.image_processor = None

    def process(self, dataset: Dataset) -> Dataset:
        return dataset.map(
            self._extract_features,
            batched=True,
            remove_columns=["text", "type", "source"],
            num_proc=self.config["num_workers"]
        )

    def _extract_features(self, examples) -> Dict:
        features = []
        for text, dtype in zip(examples["text"], examples["type"]):
            try:
                if dtype == "text":
                    features.append(self.text_processor(text))
                elif dtype == "image":
                    features.append(self.image_processor(text) if self.image_processor else self._default_feature())
                elif dtype == "video":
                    features.append(self._process_video(text) if self.image_processor else self._default_feature())
                else:
                    features.append(self._default_feature())
            except Exception:
                features.append(self._default_feature())
        return {"features": features}

    def _process_video(self, path: str) -> np.ndarray:
        cap = cv2.VideoCapture(path)
        features = []
        frame_count = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % self.config["frame_interval"] == 0:
                    frame_path = os.path.join(tmp_dir, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_path, frame)
                    features.append(self.image_processor(frame_path))
                frame_count += 1
        cap.release()
        return np.mean(features, axis=0) if features else self._default_feature()

    def _default_feature(self) -> np.ndarray:
        return np.zeros(768, dtype=np.float32)

class TextProcessor:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.max_length = 512
    def __call__(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, max_length=self.max_length, truncation=True, padding="max_length", return_tensors="np")
        combined = np.concatenate([inputs["input_ids"], inputs["attention_mask"]], axis=-1).squeeze()
        return combined.astype(np.float32) if combined.ndim == 1 else combined[0].astype(np.float32)

class ImageProcessor:
    def __init__(self, model_path: Optional[str], logger: logging.Logger = None):
        self.logger = logger
        self.extractor = None
        if model_path:
            try:
                self.extractor = ViTFeatureExtractor.from_pretrained(model_path)
            except Exception as e:
                if logger:
                    logger.warning(f"🖼️ 图像处理器初始化失败: {str(e)}")
    def __call__(self, path: str) -> np.ndarray:
        if not self.extractor:
            return np.zeros(768, dtype=np.float32)
        try:
            image = cv2.imread(path)
            if image is None:
                return np.zeros(768, dtype=np.float32)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            inputs = self.extractor(images=image_rgb, return_tensors="np")
            result = inputs["pixel_values"].squeeze().astype(np.float32)
            return result.flatten()[:768] if result.ndim > 1 else result
        except Exception as e:
            if self.logger:
                self.logger.warning(f"🖼️ 图像处理失败 {path}: {str(e)}")
            return np.zeros(768, dtype=np.float32)

# ==================== 模型训练 ====================
class ModelTrainer:
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.args = self._prepare_training_args()

    def _prepare_training_args(self) -> TrainingArguments:
        return TrainingArguments(
            output_dir=self.config["output_dir"],
            per_device_train_batch_size=self.config["batch_size"],
            num_train_epochs=self.config["epochs"],
            learning_rate=self.config["learning_rate"],
            save_strategy="epoch",
            fp16=self.config["fp16"],
            gradient_checkpointing=self.config["gradient_checkpointing"],
            logging_dir=os.path.join(self.config["output_dir"], "logs"),
            report_to=["tensorboard"],
            remove_unused_columns=False,
            dataloader_num_workers=self.config["num_workers"],
            logging_steps=10,
            save_total_limit=self.config.get("save_total_limit", 3),
            evaluation_strategy="no",
            warmup_steps=100,
            weight_decay=0.01,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            gradient_accumulation_steps=2,
            dataloader_pin_memory=True,
            auto_find_batch_size=False,
            max_grad_norm=1.0,
            seed=42
        )

    def train(self, model: AutoModelForCausalLM, dataset: Dataset):
        try:
            trainer = Trainer(
                model=model,
                args=self.args,
                train_dataset=dataset,
                data_collator=self._dynamic_collator
            )
            self.logger.info("🔥 开始模型训练...")
            train_result = trainer.train()
            trainer.save_model(self.config["output_dir"])
            trainer.save_state()
            metrics = train_result.metrics
            self.logger.info(f"✅ 训练完成 | 耗时: {metrics['train_runtime']:.2f}s | 样本数: {metrics['train_samples']}")
            return metrics
        except Exception as e:
            self.logger.error(f"❌ 训练失败: {str(e)}", exc_info=True)
            raise

    def _dynamic_collator(self, features):
        max_len = max(len(f["features"]) for f in features)
        padded = [np.pad(f["features"], (0, max_len - len(f["features"]))).astype(np.float32) for f in features]
        return {"input_ids": torch.tensor(np.array(padded, dtype=np.float32))}

# ==================== 模型部署 ====================
class ModelDeployer:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    def deploy(self, model, tokenizer, output_dir: str):
        app = FastAPI(title="AI模型推理服务")
        @app.post("/predict")
        async def predict(request: PredictionRequest):
            inputs = tokenizer(request.text, return_tensors="pt").to(model.device)
            outputs = model.generate(**inputs, max_length=512)
            return {"result": tokenizer.decode(outputs[0])}
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        self.logger.info("🌐 API服务运行中: http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)

class PredictionRequest(BaseModel):
    text: str

# ==================== 辅助函数 ====================
def create_default_config():
    default_config = {
        "model_path": "gpt2",
        "data_dir": "./data",
        "output_dir": "./output",
        "batch_size": 2,
        "epochs": 3,
        "learning_rate": 5e-5,
        "fp16": True,
        "gradient_checkpointing": True,
        "auto_deploy": False,
        "enable_image": False,
        "enable_video": False,
        "image_model_path": "google/vit-base-patch16-224",
        "frame_interval": 5,
        "num_workers": 4,
        "save_total_limit": 3,
        "max_length": 512
    }
    Path("./data").mkdir(exist_ok=True)
    Path("./output").mkdir(exist_ok=True)
    with open("config.json", 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    with open("./data/example.txt", 'w', encoding='utf-8') as f:
        f.write("这是一个示例训练样本。\nAI训练系统支持多模态数据。\n文本、图像、视频都可以处理。\n")
    with open("./data/example.csv", 'w', encoding='utf-8') as f:
        f.write('text,category\n"欢迎使用AI系统","greeting"\n"多模态训练","feature"\n')
    return default_config

def print_banner():
    print("=" * 70)
    print("全功能AI训练系统 v6.0 - 终极融合版")
    print("功能：文本/图像/视频多模态 | 并行处理 | 混合精度训练 | API部署")
    print("=" * 70)

# ==================== 主入口 ====================
if __name__ == "__main__":
    try:
        print_banner()
        config = create_default_config()
        print("✅ 默认配置文件已创建: config.json")
        print("✅ 示例数据已生成: data/example.txt, data/example.csv")
        system = AITrainingSystem("config.json")
        result = system.run_pipeline()
        print("\n🎉 训练流程成功完成！")
        print(f"📁 模型保存位置: {result['model_path']}")
        print(f"📄 日志文件: {result['log_file']}")
        if config["auto_deploy"]:
            print("🌐 API服务已启动: http://localhost:8000/docs")
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    except Exception as e:
        print(f"💥 系统运行失败: {str(e)}")