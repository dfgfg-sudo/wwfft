"""
﻿# -*- coding: utf-8 -*-
\"\"\"
Trae CN 配置管理工具 - 整合版
Trae CN Configuration Manager - Integrated Version

包含功能:
1. 模型配置修复与导出
2. 认证设置管理
3. 一键配置更新

版本: 1.0.0
生成时间: 2026-06-17

import yaml
import os
import json
from datetime import datetime

class TraeConfigManager:
    def __init__(self):
        self.config_path = "./config/openclaw_config.yaml"
        self.trae_config_dir = os.path.expandvars("%APPDATA%\\\\Trae CN")
        self.models_config_file = "trae_models_config.json"
        self.config = {}
        self.providers = {}
        self.trae_models = []
    
    def load_config(self):
        if not os.path.exists(self.config_path):
            print(f"配置文件不存在: {self.config_path}")
            return False
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            self.providers = self.config.get("providers", {})
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def show_providers_info(self):
        print("="*70)
        print("          当前配置的服务商和模型")
        if not self.providers:
            print("未配置任何服务商")
            return
        for provider_name, provider_config in self.providers.items():
            print(f"\\n服务商: {provider_config.get('name', provider_name)}")
            has_key = bool(provider_config.get("api_key"))
            print(f"  API密钥: {'已配置' if has_key else '未配置'}")
            print(f"  模型数量: {len(provider_config.get('models', []))}")
            for idx, model in enumerate(provider_config.get("models", []), 1):
                print(f"    {idx}. {model}")
    
    def export_models_config(self):
            provider_display_name = provider_config.get("name", provider_name)
            api_key = provider_config.get("api_key", "")
            for model_id in provider_config.get("models", []):
                self.trae_models.append({
                    "name": model_id,
                    "provider": provider_display_name,
                    "provider_key": provider_name,
                    "model_id": model_id,
                    "api_key": api_key,
                    "base_url": provider_config.get("base_url", "")
                })
        with open(self.models_config_file, "w", encoding="utf-8") as f:
            json.dump(self.trae_models, f, ensure_ascii=False, indent=2)
        print(f"模型配置已导出到 {self.models_config_file}")
    
    def update_trae_config(self):
        os.makedirs(self.trae_config_dir, exist_ok=True)
        trae_config_path = os.path.join(self.trae_config_dir, "models.json")
        config_data = {
            "providers": self.providers,
            "models": self.trae_models,
            "updated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        with open(trae_config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"Trae CN 配置已更新: {trae_config_path}")
    
    def setup_auth(self):
        print("\\n" + "="*70)
        print("          认证配置设置")
        auth_config = {
            "auth_method": "api_key",
            "providers": {},
            "created_at": datetime.now().isoformat()
            auth_config["providers"][provider_name] = {
                "name": provider_config.get("name", provider_name),
                "has_api_key": bool(provider_config.get("api_key")),
        auth_file = "trae_auth_config.json"
        with open(auth_file, "w", encoding="utf-8") as f:
            json.dump(auth_config, f, ensure_ascii=False, indent=2)
        print(f"认证配置已保存到 {auth_file}")
    
    def run(self):
        print("        Trae CN 配置管理工具 v1.0.0")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        if not self.load_config():
        self.show_providers_info()
        print("配置文件检查完成！")
        self.export_models_config()
        self.update_trae_config()
        self.setup_auth()
        print("所有配置已完成！请重启 Trae CN 软件。")

def main():
    manager = TraeConfigManager()
    manager.run()

if __name__ == "__main__":
    main()

"""
