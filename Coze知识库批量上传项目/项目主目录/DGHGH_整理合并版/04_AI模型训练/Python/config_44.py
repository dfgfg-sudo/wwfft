import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, PeftModel
from .config import NeuroConfig
from .security import QuantumSecurity
import psutil

class NeuroCore:
    def __init__(self, config: NeuroConfig):
        self.config = config
        self.security = QuantumSecurity(config)
        self.model, self.tokenizer = self._init_model()
        self.memory = None  # 可选记忆

    def _init_model(self):
        # 加载基础模型
        model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16
            ) if torch.cuda.is_available() else None,
            device_map="auto" if torch.cuda.is_available() else None
        )
        tokenizer = AutoTokenizer.from_pretrained(self.config.base_model)
        tokenizer.pad_token = tokenizer.eos_token

        # 检查是否有LoRA适配器
        adapter_path = self.config.output_dir / "adapter"
        if adapter_path.exists():
            model = PeftModel.from_pretrained(model, str(adapter_path))
        else:
            peft_config = LoraConfig(
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                target_modules=["q_proj", "v_proj"],
                task_type="CAUSAL_LM"
            )
            model = get_peft_model(model, peft_config)
        return model, tokenizer

    def train(self, dataset):
        from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
        tokenized = dataset.map(
            lambda x: self.tokenizer(
                x["text"],
                max_length=self.config.max_length,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            ),
            batched=True,
            remove_columns=dataset.column_names
        )
        args = TrainingArguments(
            output_dir=str(self.config.output_dir),
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.grad_accum,
            num_train_epochs=self.config.max_epochs,
            learning_rate=self.config.base_lr,
            save_strategy="epoch",
            fp16=torch.cuda.is_available(),
            logging_dir=str(self.config.cache_dir / "logs")
        )
        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=tokenized,
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False)
        )
        trainer.train()
        self.model.save_pretrained(self.config.output_dir / "adapter")
        self._secure_save()

    def _secure_save(self):
        # 加密保存模型bin文件
        for file in self.config.output_dir.glob("*.bin"):
            self.security.encrypt_file(file)
            file.unlink()

    def generate(self, prompt, max_new_tokens=100):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)