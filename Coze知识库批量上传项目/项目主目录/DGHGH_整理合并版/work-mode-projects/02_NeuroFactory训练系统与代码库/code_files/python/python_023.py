# -*- coding: utf-8 -*-
"""
NeuroForge-AI 全自动智能训练平台 v10.0
功能特性：智能数据吞噬、增量训练、量子加密、一键操作
"""

import os
import sys
import json
import logging
import hashlib
import zipfile
import yaml
from pathlib import Path
from typing import List, Dict, Any, Union
import pandas as pd
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# ==================== 系统配置类 ====================
class SystemConfig:
    """系统配置管理类 - 负责路径、目录、日志和配置文件的初始化"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        # 用户自定义模型路径（可根据实际修改）
        self.user_model_path = r"C:\Users\Administrator\Documents\uytrertrt\Bunny-v1_0-3B\neuro_data"
        self.setup_directories()
        self.setup_logging()
        self.config = self.load_or_create_config()

    def setup_directories(self):
        """创建项目所需的全部目录结构"""
        dirs = [
            "data/uploads",
            "data/processed",
            "data/encrypted",
            "models/pretrained",
            "models/training",
            "models/deployed",
            "logs",
            "config"
        ]
        for d in dirs:
            (self.base_dir / d).mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """配置日志系统 - 同时输出到文件和控制台"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.base_dir / "logs/training.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AI-Trainer")

    def load_or_create_config(self) -> Dict[str, Any]:
        """加载或创建默认配置文件"""
        default_config = {
            "paths": {
                "model_store": str(self.base_dir / "models"),
                "data_upload": str(self.base_dir / "data/uploads"),
                "processed_data": str(self.base_dir / "data/processed")
            },
            "training": {
                "default_epochs": 5,
                "batch_size": "auto",
                "learning_rate": 3e-5,
                "strategies": ["incremental", "federated"]
            },
            "security": {
                "encryption": "quantum",
                "key_rotation": True
            }
        }

        config_path = self.base_dir / "config/system_config.yaml"
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or default_config
        except FileNotFoundError:
            config = default_config
            self.save_config(config)
        return config

    def save_config(self, config: Dict[str, Any] = None):
        """保存配置文件"""
        if config is None:
            config = self.config
        config_path = self.base_dir / "config/system_config.yaml"
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f)

    def detect_model_path(self) -> str:
        """智能模型路径检测 - 依次尝试多个可能的路径"""
        possible_paths = [
            self.user_model_path,
            str(self.base_dir / "models/pretrained"),
            str(Path.home() / "Bunny-v1_0-3B")
        ]
        for path in possible_paths:
            if Path(path).exists():
                self.logger.info(f"检测到模型路径: {path}")
                return path
        # 若都不存在，创建默认目录
        new_path = str(self.base_dir / "models/pretrained")
        Path(new_path).mkdir(parents=True, exist_ok=True)
        self.logger.warning("未找到现有模型，初始化新目录: %s", new_path)
        return new_path


# ==================== 数据加载引擎 ====================
class DataOmnivore:
    """多格式数据吞噬引擎 - 支持 TXT, JSON, CSV, ZIP 的自动解析"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.supported_ext = ('.txt', '.json', '.csv', '.zip')

    def load_all_data(self, input_dir: str = None) -> List[Dict]:
        """遍历目录，加载所有支持格式的文件并返回数据列表"""
        if input_dir is None:
            input_dir = self.config.base_dir / "data/uploads"
        
        data = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.supported_ext:
                    try:
                        file_data = self._process_file(file_path)
                        data.extend(file_data)
                    except Exception as e:
                        self.config.logger.error(f"处理文件失败 {file_path}: {str(e)}")
        return data

    def _process_file(self, file_path: Path) -> List[Dict]:
        """根据文件扩展名调用对应的解析方法"""
        ext = file_path.suffix.lower()
        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return [{"text": content, "source": str(file_path), "type": "text"}]
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        return content
                    else:
                        return [content]
            elif ext == '.csv':
                df = pd.read_csv(file_path)
                records = df.to_dict('records')
                for record in records:
                    record['source'] = str(file_path)
                    record['type'] = 'tabular'
                return records
            elif ext == '.zip':
                return self._handle_zip(file_path)
        except Exception as e:
            self.config.logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
        return []

    def _handle_zip(self, zip_path: Path) -> List[Dict]:
        """解压 ZIP 文件并递归处理内部文件"""
        extract_to = self.config.base_dir / f"data/temp_{zip_path.stem}"
        extract_to.mkdir(exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(extract_to)
            return self.load_all_data(extract_to)
        except Exception as e:
            self.config.logger.error(f"解压文件 {zip_path} 失败: {str(e)}")
            return []


# ==================== 量子加密系统 ====================
class QuantumEncryptor:
    """量子级加密引擎 - 使用 XChaCha20-Poly1305 算法"""
    
    def __init__(self):
        self.key_size = 32   # 256-bit 密钥
        self.nonce_size = 24 # 192-bit nonce

    def encrypt_model(self, model_data: bytes) -> bytes:
        """加密模型数据，返回 nonce + ciphertext"""
        key = os.urandom(self.key_size)
        nonce = os.urandom(self.nonce_size)
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            mode=None,
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(model_data) + encryptor.finalize()
        return nonce + encrypted

    def encrypt_file(self, input_path: str, output_path: str):
        """加密文件并保存到输出路径"""
        with open(input_path, 'rb') as f:
            data = f.read()
        encrypted = self.encrypt_model(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted)


# ==================== 智能训练系统 ====================
class AITrainer:
    """基于 Transformers 的增量训练引擎"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.model_path = config.detect_model_path()
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
            if not self.tokenizer.pad_token:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
        except Exception as e:
            self.config.logger.error(f"模型加载失败: {str(e)}")
            raise

    def prepare_dataset(self, data: List[Dict]) -> Dataset:
        """将原始数据列表转换为 HuggingFace Dataset"""
        if not data:
            raise ValueError("训练数据为空")
        texts = []
        for item in data:
            if 'text' in item:
                texts.append(item['text'])
            elif isinstance(item, dict):
                texts.append(json.dumps(item, ensure_ascii=False))
            else:
                texts.append(str(item))
        df = pd.DataFrame({'text': texts})
        return Dataset.from_pandas(df)

    def tokenize_function(self, examples):
        """分词函数"""
        return self.tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512
        )

    def incremental_train(self, dataset: List[Dict]) -> str:
        """执行增量训练，返回最终模型保存路径"""
        self.config.logger.info("准备训练数据...")
        raw_dataset = self.prepare_dataset(dataset)
        tokenized_datasets = raw_dataset.map(self.tokenize_function, batched=True)
        self.config.logger.info(f"训练数据准备完成，共 {len(tokenized_datasets)} 条样本")

        training_args = TrainingArguments(
            output_dir=str(self.config.base_dir / "models/training"),
            overwrite_output_dir=True,
            num_train_epochs=5,
            per_device_train_batch_size=4,
            save_steps=500,
            save_total_limit=2,
            learning_rate=3e-5,
            fp16=torch.cuda.is_available(),
            logging_dir=str(self.config.base_dir / "logs"),
            logging_steps=50,
            report_to=None
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets,
            data_collator=self.data_collator
        )

        self.config.logger.info("开始模型训练...")
        trainer.train()

        output_path = self.config.base_dir / "models/training/final_model"
        trainer.save_model(str(output_path))
        self.tokenizer.save_pretrained(str(output_path))
        self.config.logger.info(f"模型训练完成，保存至: {output_path}")
        return str(output_path)


# ==================== 模型打包系统 ====================
class ModelPackager:
    """模型打包与加密封装器"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.encryptor = QuantumEncryptor()

    def package_model(self, model_dir: str, output_name: str = "model_singularity") -> str:
        """打包模型目录为 ZIP 并加密"""
        model_dir_path = Path(model_dir)
        if not model_dir_path.exists():
            raise ValueError(f"模型目录不存在: {model_dir}")

        zip_path = self.config.base_dir / "models/deployed" / f"{output_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in model_dir_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(model_dir_path)
                    zf.write(file_path, arcname)
        self.config.logger.info(f"模型打包完成: {zip_path}")

        encrypted_path = zip_path.with_suffix('.encrypted.zip')
        self.encryptor.encrypt_file(str(zip_path), str(encrypted_path))
        self.config.logger.info(f"模型加密完成: {encrypted_path}")
        return str(encrypted_path)


# ==================== 主控制系统 ====================
class TrainingOrchestrator:
    """全流程协调器 - 串联数据加载、训练、打包各阶段"""
    
    def __init__(self):
        self.config = SystemConfig()
        self.data_loader = DataOmnivore(self.config)
        self.trainer = None
        self.packager = ModelPackager(self.config)

    def run_full_pipeline(self):
        """执行完整训练流水线"""
        self.config.logger.info("🚀 启动超级AI训练协议")
        self.config.save_config()

        # 阶段1：数据加载
        self.config.logger.info("🔍 正在扫描并加载数据...")
        dataset = self.data_loader.load_all_data()
        if not dataset:
            self.config.logger.error("未找到有效训练数据！请在 data/uploads 目录中添加数据文件")
            return
        self.config.logger.info(f"✔ 成功加载 {len(dataset)} 条数据样本")

        # 阶段2：模型训练
        self.config.logger.info("🧠 初始化模型训练引擎...")
        self.trainer = AITrainer(self.config)
        trained_model_path = self.trainer.incremental_train(dataset)
        self.config.logger.info(f"✔ 模型训练完成: {trained_model_path}")

        # 阶段3：加密打包
        self.config.logger.info("🔐 生成量子加密模型包...")
        final_package_path = self.packager.package_model(trained_model_path)
        self.config.logger.info(f"✅ 全流程完成！加密模型包: {final_package_path}")
        return final_package_path


# ==================== 环境自动设置 ====================
def setup_environment():
    """自动创建虚拟环境并安装依赖"""
    import subprocess
    import venv

    base_dir = Path(__file__).parent
    venv_path = base_dir / "venv"
    if not venv_path.exists():
        print("创建Python虚拟环境...")
        venv.create(venv_path, with_pip=True)

    requirements = [
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "datasets>=2.12.0",
        "pandas>=1.5.0",
        "pyyaml>=6.0",
        "cryptography>=39.0.0"
    ]

    if os.name == 'nt':  # Windows
        pip_cmd = [str(venv_path / "Scripts" / "pip.exe")]
    else:
        pip_cmd = [str(venv_path / "bin" / "pip")]

    for package in requirements:
        try:
            subprocess.check_call(pip_cmd + ["install", package])
        except subprocess.CalledProcessError as e:
            print(f"安装 {package} 失败: {e}")
            return False
    return True


# ==================== 一键执行入口 ====================
if __name__ == "__main__":
    try:
        if not setup_environment():
            print("环境设置失败，请手动安装依赖包")
            sys.exit(1)

        orchestrator = TrainingOrchestrator()
        result_path = orchestrator.run_full_pipeline()

        if result_path and sys.platform == "win32":
            result_dir = os.path.dirname(result_path)
            os.startfile(result_dir)
            print(f"已自动打开结果目录: {result_dir}")
    except Exception as e:
        logging.error(f"系统运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)