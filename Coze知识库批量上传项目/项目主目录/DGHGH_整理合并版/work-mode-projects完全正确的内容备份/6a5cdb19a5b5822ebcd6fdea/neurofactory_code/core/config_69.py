import os
from pathlib import Path
from cryptography.fernet import Fernet

class NeuroConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        # 模型与路径
        self.base_model = os.getenv("BASE_MODEL", "gpt2")
        self.data_paths = [Path(p) for p in os.getenv("DATA_PATHS", "./data").split(",")]
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        self.cache_dir = Path(os.getenv("CACHE_DIR", "./cache"))
        self.model_dir = Path(os.getenv("MODEL_DIR", "./models"))

        # 训练超参数
        self.max_length = int(os.getenv("MAX_LENGTH", "1024"))
        self.lora_r = int(os.getenv("LORA_R", "16"))
        self.lora_alpha = int(os.getenv("LORA_ALPHA", "64"))
        self.grad_accum = int(os.getenv("GRAD_ACCUM", "8"))
        self.max_epochs = int(os.getenv("MAX_EPOCHS", "5"))
        self.base_lr = float(os.getenv("BASE_LR", "3e-5"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "4"))

        # 安全密钥
        self.encrypt_key = os.getenv("ENCRYPT_KEY", Fernet.generate_key().decode())
        self.quantum_key = self.encrypt_key.encode()

        # 创建目录
        for p in [self.output_dir, self.cache_dir, self.model_dir]:
            p.mkdir(parents=True, exist_ok=True)