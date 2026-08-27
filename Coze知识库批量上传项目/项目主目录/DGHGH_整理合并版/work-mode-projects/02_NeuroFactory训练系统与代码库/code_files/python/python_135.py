def load_model(self, project_path):
       # 验证模型文件完整性
       required_files = ["config.json", "model.safetensors"]
       # 分步加载确保可靠性
       config = AutoConfig.from_pretrained(str(model_dir))
       model = AutoModelForCausalLM.from_config(config)
       state_dict = load_file(str(model_dir / "model.safetensors"))