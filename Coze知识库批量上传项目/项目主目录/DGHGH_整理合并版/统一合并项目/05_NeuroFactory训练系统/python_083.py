import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MultiModalConfig:
    project_name: str = "AutoMultiModal AI Training System"
    project_version: str = "1.0.0"
    author: str = "AMM-ATS Team"

    data_dir: str = "./data"
    train_split: str = "train"
    val_split: str = "val"
    test_split: str = "test"
    image_size: int = 224
    batch_size: int = 32
    num_workers: int = 4
    max_text_length: int = 128

    text_model_name: str = "bert-base-uncased"
    image_model_name: str = "resnet50"
    hidden_size: int = 768
    num_classes: int = 10
    dropout_rate: float = 0.1
    pretrained: bool = True
    freeze_text_encoder: bool = False
    freeze_image_encoder: bool = False

    learning_rate: float = 1e-4
    epochs: int = 100
    warmup_epochs: int = 5
    weight_decay: float = 1e-4
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0

    optimizer_type: str = "adamw"
    scheduler_type: str = "cosine"

    checkpoint_dir: str = "./checkpoints"
    output_dir: str = "./outputs"
    log_dir: str = "./logs"
    tensorboard_dir: str = "./runs"

    experiment_name: str = "exp_001"
    seed: int = 42
    device: str = "auto"

    use_amp: bool = True
    early_stopping_patience: int = 10
    save_best_only: bool = True
    eval_strategy: str = "epoch"
    logging_steps: int = 10
    save_steps: int = 100

    def __post_init__(self):
        import torch
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        for d in [self.checkpoint_dir, self.output_dir, self.log_dir, self.tensorboard_dir]:
            os.makedirs(d, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def save(self, path: str):
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> "MultiModalConfig":
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)