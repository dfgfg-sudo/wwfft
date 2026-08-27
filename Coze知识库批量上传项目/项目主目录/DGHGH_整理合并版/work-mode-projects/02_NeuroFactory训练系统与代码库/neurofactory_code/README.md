# 🧠 NeuroFactory 智能训练系统 - 完整可运行代码

## 项目结构

```
neurofactory_code/
├── main.py              # 主入口（GUI/CLI双模式）
├── requirements.txt     # Python依赖
├── config.yaml         # 系统配置
├── core/
│   ├── config.py       # 统一配置管理
│   ├── security.py     # 量子安全加密
│   ├── processor.py    # 多格式数据处理
│   ├── model_core.py   # 模型核心（LoRA/4-bit）
│   ├── memory.py       # FAISS向量记忆
│   ├── training.py     # 训练流程协调
│   ├── optimizer.py    # 动态优化器
│   └── api_service.py  # REST API服务
├── gui/
│   └── main_window.py  # 图形界面
├── analysis/
│   └── project_analyzer.py  # 项目分析
└── utils/
    └── file_utils.py   # 工具函数
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动系统

```bash
# 命令行模式
python main.py

# GUI模式
python main.py --gui

# 指定配置
python main.py --config config.yaml --gui
```

## 核心功能

1. **多源数据AI模型训练** - 支持317+文件格式
2. **量子安全加密** - AES-256/Fernet军事级安全
3. **Coze插件集成** - OpenAPI 3.0规范管理
4. **自动训练流水线** - 端到端全自动化
5. **学习认证体系** - Python/AI/全栈认证

## 技术栈

- PyTorch + Transformers (模型训练)
- FAISS (向量检索)
- FastAPI (API服务)
- watchdog (文件监控)
- cryptography (加密)
- scikit-learn (机器学习)
- tkinter (图形界面)
