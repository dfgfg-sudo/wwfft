import os
import sys
import json
import logging
import argparse
from datetime import datetime
import numpy as np
import torch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MultiModalConfig
from data.dataset import MultiModalDataLoader
from models.model import MultiModalModel
from training.trainer import MultiModalTrainer

class AutoMultiModalSystem:
    def __init__(self, config_path=None):
        self.config = MultiModalConfig.load(config_path) if config_path else MultiModalConfig()
        self._set_seed(self.config.seed)
        self.data_loader = None
        self.model = None
        self.trainer = None
        self.is_initialized = False
        logging.info(f"系统初始化，实验: {self.config.experiment_name}，设备: {self.config.device}")

    def _set_seed(self, seed):
        import random
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    def initialize(self):
        logging.info("初始化数据加载器...")
        self.data_loader = MultiModalDataLoader(self.config)
        self.data_loader.prepare_datasets()
        self.data_loader.prepare_dataloaders()

        logging.info("初始化模型...")
        self.model = MultiModalModel(self.config)

        logging.info("初始化训练器...")
        self.trainer = MultiModalTrainer(self.config, self.model)

        self.is_initialized = True
        logging.info("系统初始化完成")

    def train(self, resume_from=None):
        if not self.is_initialized:
            self.initialize()
        if resume_from:
            ckpt_path = os.path.join(self.config.checkpoint_dir, resume_from)
            if os.path.exists(ckpt_path):
                self.trainer.load_checkpoint(ckpt_path)
        train_loader = self.data_loader.get_dataloader('train')
        val_loader = self.data_loader.get_dataloader('val')
        self.trainer.train(train_loader, val_loader)

    def evaluate(self, checkpoint_path=None):
        if not self.is_initialized:
            self.initialize()
        if checkpoint_path:
            self.trainer.load_checkpoint(os.path.join(self.config.checkpoint_dir, checkpoint_path))
        test_loader = self.data_loader.get_dataloader('test')
        metrics = self.trainer.evaluate(test_loader)
        self._save_eval_results(metrics)
        return metrics

    def predict(self, data_path=None, checkpoint_path=None):
        if not self.is_initialized:
            self.initialize()
        if checkpoint_path:
            self.trainer.load_checkpoint(os.path.join(self.config.checkpoint_dir, checkpoint_path))
        loader = self.data_loader.get_dataloader('test')
        results = self.trainer.predict(loader)
        self._save_predictions(results)
        return results

    def export_model(self, format='onnx', checkpoint_path=None):
        if not self.is_initialized:
            self.initialize()
        if checkpoint_path:
            self.trainer.load_checkpoint(os.path.join(self.config.checkpoint_dir, checkpoint_path))
        export_dir = os.path.join(self.config.output_dir, 'exported_models')
        os.makedirs(export_dir, exist_ok=True)
        if format == 'onnx':
            self._export_onnx(export_dir)
        elif format == 'torchscript':
            self._export_torchscript(export_dir)
        elif format == 'huggingface':
            self._export_huggingface(export_dir)
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def _export_onnx(self, export_dir):
        dummy_img = torch.randn(1, 3, self.config.image_size, self.config.image_size)
        dummy_ids = torch.randint(0, 10000, (1, self.config.max_text_length))
        dummy_mask = torch.ones(1, self.config.max_text_length)
        path = os.path.join(export_dir, 'model.onnx')
        torch.onnx.export(self.model, (dummy_img, dummy_ids, dummy_mask), path,
                          input_names=['image','input_ids','attention_mask'],
                          output_names=['logits','features'],
                          dynamic_axes={'image':{0:'batch'}, 'input_ids':{0:'batch'}, 'attention_mask':{0:'batch'}},
                          opset_version=13)
        logging.info(f"ONNX 导出至: {path}")

    def _export_torchscript(self, export_dir):
        dummy_img = torch.randn(1, 3, self.config.image_size, self.config.image_size)
        dummy_ids = torch.randint(0, 10000, (1, self.config.max_text_length))
        dummy_mask = torch.ones(1, self.config.max_text_length)
        scripted = torch.jit.trace(self.model, (dummy_img, dummy_ids, dummy_mask))
        path = os.path.join(export_dir, 'model.pt')
        scripted.save(path)
        logging.info(f"TorchScript 导出至: {path}")

    def _export_huggingface(self, export_dir):
        hf_dir = os.path.join(export_dir, 'huggingface')
        os.makedirs(hf_dir, exist_ok=True)
        self.model.save_pretrained(hf_dir)
        self.config.save(os.path.join(hf_dir, 'config.json'))
        from transformers import BertTokenizer
        tokenizer = BertTokenizer.from_pretrained(self.config.text_model_name)
        tokenizer.save_pretrained(hf_dir)
        logging.info(f"HuggingFace 导出至: {hf_dir}")

    def _save_eval_results(self, metrics):
        path = os.path.join(self.config.output_dir, 'evaluation_results.json')
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2)

    def _save_predictions(self, results):
        path = os.path.join(self.config.output_dir, 'predictions.npz')
        np.savez(path, **results)
        logging.info(f"预测结果保存至: {path}")