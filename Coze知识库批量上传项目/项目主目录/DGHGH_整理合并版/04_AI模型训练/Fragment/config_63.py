"""
neurofactory/
├── main.py                         # 主入口（GUI/CLI）
├── requirements.txt                # 全部依赖
├── config.yaml                     # 统一配置（含模型、训练、安全、监控）
├── README.md                       # 项目说明
├── core/
│   ├── __init__.py
│   ├── config.py                   # 单例配置管理（NeuroConfig）
│   ├── security.py                 # 量子加密（Fernet + AES）
│   ├── processor.py                # 多格式数据处理（支持TXT/CSV/JSON/PDF/DOCX）
│   ├── model_core.py               # 模型加载、LoRA、4-bit量化训练
│   ├── memory.py                   # FAISS向量记忆系统
│   ├── training.py                 # 训练流程协调（TrainingSystem）
│   └── optimizer.py                # 动态优化器与学习率调度
├── analysis/
│   ├── __init__.py
│   ├── project_analyzer.py         # 项目结构、依赖、质量分析
│   └── data_analyzer.py            # 数据完整性、准确性、异常检测
├── gui/
│   ├── __init__.py
│   ├── main_window.py              # 主窗口与菜单
│   ├── training_tab.py             # 训练参数与启停
│   ├── monitor_tab.py              # GPU/CPU/内存实时监控
│   ├── export_tab.py               # 模型导出与加密
│   ├── chat_tab.py                 # 对话测试
│   ├── preferences_dialog.py       # 偏好设置
│   ├── data_analysis_dialog.py     # 数据质量报告
│   └── model_evaluation_dialog.py  # 模型评估
├── utils/
│   ├── __init__.py
│   ├── file_utils.py               # 文件读写、备份、压缩
│   ├── crypto_utils.py             # 加解密、哈希
│   ├── monitor_utils.py            # 系统资源采集
│   └── validation_utils.py         # 数据校验
├── tests/
│   └── test_core.py                # 单元测试（配置、加密）
├── docs/
│   └── user_guide.md               # 用户手册
├── data/                           # 运行时数据（自动创建）
├── models/                         # 模型存储（自动创建）
└── logs/                           # 日志（自动创建）
"""
