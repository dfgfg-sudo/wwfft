# -*- coding: utf-8 -*-
"""
配置管理系统
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_path = self._get_base_path()
        self.config = self._load_config(config_path)
        self._setup_paths()
        
    def _get_base_path(self) -> Path:
        """获取基础路径"""
        possible_paths = [
            Path(r"C:\Users\Administrator\Documents\uytrertrt\Bunny-v1_0-3B"),
            Path.cwd(),
            Path.home() / "Documents" / "UltimateAI"
        ]
        
        for path in possible_paths:
            if path.exists():
                logging.info(f"使用基础路径: {path}")
                return path
                
        raise FileNotFoundError("未找到有效的基础路径")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = self._get_default_config()
        
        # 如果提供了配置路径
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                    return self._deep_merge(default_config, user_config)
                except Exception as e:
                    logging.warning(f"加载用户配置失败: {e}")
                    
        # 检查默认配置路径
        default_config_path = self.base_path / "config.json"
        if default_config_path.exists():
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                return self._deep_merge(default_config, user_config)
            except Exception as e:
                logging.warning(f"加载默认配置失败: {e}")
                
        return default_config
        
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "system": {
                "name": "UltimateAI-System-v9.0",
                "version": "9.0.0",
                "description": "量子神经架构全栈AI系统",
                "author": "AI Research Team"
            },
            "paths": {
                "data_dir": "data",
                "model_dir": "models",
                "log_dir": "logs",
                "output_dir": "outputs",
                "cache_dir": ".cache"
            },
            "quantum": {
                "qubits": 1024,
                "topology": "hypercube",
                "error_correction": "surface_code",
                "enabled": True
            },
            "multimodal": {
                "text_model": "bert-base-uncased",
                "image_model": "resnet50",
                "audio_model": "wav2vec2",
                "fusion_method": "cross_attention"
            },
            "reasoning": {
                "num_experts": 8,
                "quantum_enabled": True,
                "logic_depth": 3
            },
            "consciousness": {
                "short_term_memory": 1000000,
                "long_term_memory": 1000000000000,
                "evolution_interval": 1800
            },
            "security": {
                "encryption": "post_quantum",
                "key_size": 4096,
                "encrypt_models": True,
                "anomaly_detection": True
            },
            "evolution": {
                "meta_learning": True,
                "mutation_rate": 0.15,
                "crossover_rate": 0.7,
                "architecture_search": True
            },
            "automl": {
                "max_trials": 100,
                "timeout": 86400,
                "objective": "val_accuracy"
            },
            "training": {
                "batch_size": 32,
                "epochs": 10,
                "learning_rate": 2e-5,
                "optimizer": "adamw",
                "scheduler": "cosine"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_origins": ["*"],
                "rate_limit": 100
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9090,
                "log_level": "INFO"
            }
        }
        
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def _setup_paths(self):
        """设置路径"""
        # 确保所有目录存在
        for key, rel_path in self.config['paths'].items():
            abs_path = self.base_path / rel_path
            abs_path.mkdir(parents=True, exist_ok=True)
            
    def save_config(self, path: Optional[str] = None):
        """保存配置"""
        save_path = Path(path) if path else self.base_path / "config_saved.json"
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
        logging.info(f"配置已保存到: {save_path}")
        
    def update_config(self, updates: Dict[str, Any]):
        """更新配置"""
        self.config = self._deep_merge(self.config, updates)
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value