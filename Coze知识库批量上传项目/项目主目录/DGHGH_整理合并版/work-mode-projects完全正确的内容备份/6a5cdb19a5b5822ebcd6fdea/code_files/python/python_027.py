# ========== Neuro Factory（PyQt5） ==========
import sys
import os
import json
import hashlib
import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QLabel, QLineEdit, QTabWidget,
    QSlider, QMessageBox, QProgressBar, QGroupBox, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from cryptography.fernet import Fernet
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer,
    DataCollatorForLanguageModeling, BitsAndBytesConfig, prepare_model_for_kbit_training
)
from peft import LoraConfig, get_peft_model
from datasets import Dataset
import pandas as pd

class NeuroConfig:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.base_model = "deepseek-ai/deepseek-llm-1.3b-chat"
            cls._instance.data_dirs = ["./data", "./custom_data"]
            cls._instance.output_dir = Path("./neuro_models")
            cls._instance.cache_dir = Path("./.neuro_cache")
            cls._instance.max_length = 2048
            cls._instance.batch_size = 2
            cls._instance.grad_accum = 4
            cls._instance.epochs = 3
            cls._instance.learning_rate = 2e-5
            cls._instance.lora_r = 8
            cls._instance.lora_alpha = 32
            cls._instance.encrypt_key = Fernet.generate_key().decode()
            cls._instance._prepare_directories()
        return cls._instance
    def _prepare_directories(self):
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        for d in self.data_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

class NeuroDataEngine:
    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        self.tokenizer.pad_token = self.tokenizer.eos_token
    def feed_data(self, files=None):
        all_samples = []
        for data_dir in self.config.data_dirs:
            for path in Path(data_dir).rglob("*"):
                samples = self._process_file(path)
                if samples:
                    all_samples.extend(samples)
        return Dataset.from_dict({
            "instruction": [s["instruction"] for s in all_samples],
            "output": [s["output"] for s in all_samples]
        }) if all_samples else Dataset.from_dict({})
    def _process_file(self, path):
        ext = path.suffix.lower()
        if ext == ".txt": return self._process_txt(path)
        elif ext == ".json": return self._process_json(path)
        elif ext == ".csv": return self._process_csv(path)
        return []
    def _process_txt(self, path):
        samples = []
        with open(path, "r", encoding="utf-8") as f:
            dialog = []
            for line in f:
                line = line.strip()
                if line: dialog.append(line)
                else:
                    if len(dialog) >= 2:
                        samples.append({"instruction": dialog[0].split(":",1)[-1].strip(),
                                        "output": dialog[1].split(":",1)[-1].strip()})
                    dialog = []
        return samples
    def _process_json(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return [{"instruction": k, "output": v} for k,v in data.items()]
    def _process_csv(self, path):
        df = pd.read_csv(path)
        return [{"instruction": row["question"], "output": str(row["answer"])} for _, row in df.iterrows()]

class ModelVaultNeuro:
    def __init__(self, config):
        self.cipher = Fernet(config.encrypt_key.encode())
    def secure_save(self, model, path):
        state_dict = model.state_dict()
        encrypted = {}
        for name, param in state_dict.items():
            np_param = param.cpu().numpy()
            hashed = hashlib.sha256(np_param.tobytes() + self.cipher._signing_key).digest()
            encrypted[name] = torch.from_numpy(np.frombuffer(hashed[:np_param.nbytes], dtype=np_param.dtype))
        torch.save(encrypted, path)
    def tamper_check(self, path):
        return hashlib.sha256(open(path,'rb').read()).hexdigest() != Path(path+'.hash').read_text()

class NeuroTrainerPyQt(QThread):
    update_log = pyqtSignal(str)
    training_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    def __init__(self, config, dataset):
        super().__init__()
        self.config = config
        self.dataset = dataset
        self.vault = ModelVaultNeuro(config)
    def run(self):
        try:
            model, tokenizer = self._init_model()
            tokenized = self._preprocess(tokenizer)
            args = TrainingArguments(
                output_dir=str(self.config.output_dir),
                per_device_train_batch_size=self._dynamic_batch_size(),
                gradient_accumulation_steps=self.config.grad_accum,
                num_train_epochs=self.config.epochs,
                learning_rate=self.config.learning_rate,
                fp16=torch.cuda.is_available(),
                logging_steps=50,
                save_strategy="epoch"
            )
            trainer = Trainer(model=model, args=args, train_dataset=tokenized,
                              data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False))
            trainer.train()
            self._save_model(model, tokenizer)
            self.training_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    def _init_model(self):
        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                                        bnb_4bit_compute_dtype=torch.bfloat16)
        model = AutoModelForCausalLM.from_pretrained(self.config.base_model, quantization_config=bnb_config,
                                                     device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
        tokenizer.pad_token = tokenizer.eos_token
        model = prepare_model_for_kbit_training(model)
        model = get_peft_model(model, LoraConfig(r=self.config.lora_r, lora_alpha=self.config.lora_alpha,
                                                 target_modules=["q_proj","v_proj"], task_type="CAUSAL_LM"))
        return model, tokenizer
    def _dynamic_batch_size(self):
        if torch.cuda.is_available():
            free = torch.cuda.mem_get_info()[0] / (1024**3)
            return 4 if free > 20 else 2 if free > 10 else 1
        return 1
    def _preprocess(self, tokenizer):
        return self.dataset.map(
            lambda x: tokenizer([f"Instruction: {i}\nOutput: {o}" for i,o in zip(x["instruction"], x["output"])],
                                truncation=True, max_length=self.config.max_length, padding="max_length"),
            batched=True, remove_columns=["instruction","output"]
        )
    def _save_model(self, model, tokenizer):
        out_dir = self.config.output_dir / datetime.now().strftime("%Y%m%d_%H%M")
        out_dir.mkdir()
        model.save_pretrained(out_dir)
        tokenizer.save_pretrained(out_dir)
        self.vault.secure_save(model, out_dir/"model_encrypted.bin")
        (out_dir/"model.hash").write_text(hashlib.sha256(open(out_dir/"model_encrypted.bin",'rb').read()).hexdigest())
        self.update_log.emit(f"模型已保存至 {out_dir}")

class CodeGenerator:
    TEMPLATES = {
        "web_app": {
            "main.py": "from flask import Flask\napp=Flask(__name__)\n@app.route('/')\ndef index(): return 'Hello'\nif __name__=='__main__': app.run()",
            "requirements.txt": "flask>=2.0.0"
        },
        "cli_tool": {
            "main.py": "import click\n@click.command()\ndef cli(): click.echo('Hello')\nif __name__=='__main__': cli()",
            "requirements.txt": "click>=8.0.0"
        }
    }
    def generate(self, project_type, features, output_dir):
        out = Path(output_dir)
        out.mkdir(exist_ok=True)
        for fname, content in self.TEMPLATES[project_type].items():
            (out/fname).write_text(content)
        return str(out)

class NeuroGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = NeuroConfig()
        self.data_engine = NeuroDataEngine(self.config)
        self.code_gen = CodeGenerator()
        self.trainer = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("Neuro Factory Ultimate")
        self.setGeometry(100,100,1200,800)
        tabs = QTabWidget()
        # 训练选项卡
        train_tab = QWidget()
        train_layout = QVBoxLayout()
        self.btn_load = QPushButton("加载数据")
        self.btn_train = QPushButton("开始训练")
        self.log_display = QTextEdit()
        train_layout.addWidget(self.btn_load)
        train_layout.addWidget(self.btn_train)
        train_layout.addWidget(QLabel("训练日志"))
        train_layout.addWidget(self.log_display)
        train_tab.setLayout(train_layout)
        # 代码生成选项卡
        code_tab = QWidget()
        code_layout = QVBoxLayout()
        self.project_type = QComboBox()
        self.project_type.addItems(["web_app","cli_tool"])
        self.features_input = QLineEdit("user,admin")
        self.btn_gen_code = QPushButton("生成代码")
        code_layout.addWidget(QLabel("项目类型"))
        code_layout.addWidget(self.project_type)
        code_layout.addWidget(QLabel("功能列表"))
        code_layout.addWidget(self.features_input)
        code_layout.addWidget(self.btn_gen_code)
        code_tab.setLayout(code_layout)
        # 安全选项卡
        security_tab = QWidget()
        security_layout = QVBoxLayout()
        self.btn_encrypt = QPushButton("加密文件")
        self.btn_decrypt = QPushButton("解密文件")
        security_layout.addWidget(self.btn_encrypt)
        security_layout.addWidget(self.btn_decrypt)
        security_tab.setLayout(security_layout)
        tabs.addTab(train_tab, "模型训练")
        tabs.addTab(code_tab, "代码生成")
        tabs.addTab(security_tab, "安全中心")
        self.setCentralWidget(tabs)
        self.btn_load.clicked.connect(self.load_data)
        self.btn_train.clicked.connect(self.start_training)
        self.btn_gen_code.clicked.connect(self.generate_code)
        self.btn_encrypt.clicked.connect(lambda: self.security_operation("encrypt"))
        self.btn_decrypt.clicked.connect(lambda: self.security_operation("decrypt"))
    def load_data(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择数据文件", "", "*.txt *.json *.csv")
        if files:
            try:
                self.data_engine.feed_data(files)
                self.log_display.append(f"[{datetime.now()}] 加载 {len(files)} 个文件")
            except Exception as e:
                self.log_display.append(f"[{datetime.now()}] 加载失败: {e}")
    def start_training(self):
        dataset = self.data_engine.feed_data()
        if len(dataset)==0:
            QMessageBox.critical(self, "错误", "无训练数据")
            return
        self.trainer = NeuroTrainerPyQt(self.config, dataset)
        self.trainer.update_log.connect(self.log_display.append)
        self.trainer.training_finished.connect(lambda: QMessageBox.information(self,"完成","训练完成"))
        self.trainer.error_occurred.connect(lambda msg: QMessageBox.critical(self,"错误",msg))
        self.trainer.start()
    def generate_code(self):
        project_type = self.project_type.currentText()
        features = [f.strip() for f in self.features_input.text().split(",")]
        out_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if out_dir and features:
            try:
                path = self.code_gen.generate(project_type, features, out_dir)
                self.log_display.append(f"[{datetime.now()}] 代码生成至 {path}")
            except Exception as e:
                self.log_display.append(f"[{datetime.now()}] 生成失败: {e}")
    def security_operation(self, op_type):
        file, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if not file: return
        try:
            vault = ModelVaultNeuro(self.config)
            if op_type == "encrypt":
                vault.secure_save(torch.load(file), file+".enc")
            else:
                dec = vault.cipher.decrypt(Path(file).read_bytes())
                Path(file.replace(".enc","")).write_bytes(dec)
            self.log_display.append(f"[{datetime.now()}] {op_type} 操作完成")
        except Exception as e:
            self.log_display.append(f"[{datetime.now()}] 安全操作失败: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NeuroGUI()
    win.show()
    sys.exit(app.exec_())