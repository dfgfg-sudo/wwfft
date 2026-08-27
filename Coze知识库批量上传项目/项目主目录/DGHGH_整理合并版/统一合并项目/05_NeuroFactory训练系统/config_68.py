"""
graph TD
    subgraph UI层
        GUI[SingularityUI / Tkinter 主窗口]
        TrainTab[训练标签页]
        MonitorTab[监控标签页]
        ExportTab[导出标签页]
        ChatTab[对话标签页]
        PrefDialog[偏好设置]
        AnalysisDialog[数据分析报告]
        EvalDialog[模型评估]
    end

    subgraph 核心引擎
        Config[NeuroConfig 单例配置]
        Security[QuantumSecurity 加密安全]
        Processor[NeuroDataProcessor 数据处理]
        Model[NeuroCore 模型核心]
        Memory[QuantumMemory FAISS记忆]
        Trainer[TrainingSystem 训练协调]
        Optimizer[NeuroOptimizer 优化器]
    end

    subgraph 分析模块
        ProjAnalyzer[ProjectAnalyzer 项目分析]
        DataAnalyzer[DataAnalyzer 数据质量]
    end

    subgraph 外部依赖
        Transformers[HuggingFace Transformers]
        PEFT[PEFT / LoRA]
        FAISS[FAISS 向量检索]
        PyNVML[GPU监控]
        Psutil[系统资源]
        Cryptography[Fernet 加密]
    end

    GUI --> Config
    GUI --> Trainer
    TrainTab --> Config
    TrainTab --> Trainer
    MonitorTab --> PyNVML
    MonitorTab --> Psutil
    ExportTab --> Security
    ChatTab --> Model
    PrefDialog --> Config
    AnalysisDialog --> DataAnalyzer
    EvalDialog --> Model

    Trainer --> Processor
    Trainer --> Model
    Trainer --> Security
    Trainer --> Optimizer
    Model --> Memory
    Model --> Transformers
    Model --> PEFT
    Processor --> Config
    Processor --> Security
    Memory --> FAISS

    ProjAnalyzer --> Config
    DataAnalyzer --> Processor

    Config --> Security
    Config --> Optimizer
"""
