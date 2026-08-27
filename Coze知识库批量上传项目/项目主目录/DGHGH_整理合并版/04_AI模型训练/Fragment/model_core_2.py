"""
graph TD
    subgraph "🎯 核心架构层"
        A[🏢 AIDatasetPack Pro v5.0] --> B[📁 企业级数据源]
        B --> C{🔄 自动化处理管道}
    end
    
    subgraph "🔧 智能预处理引擎"
        C --> D[🔄 FileMerger]
        D --> D1[📊 格式分析器]
        D --> D2[🔍 重复检测器]
        D --> D3[🔄 智能合并器]
        D --> D4[📈 深度内容对比器]
    end
    
    subgraph "🚀 并行压缩引擎"
        C --> E[⚡ 多线程处理器]
        E --> E1[🧵 线程池管理]
        E --> E2[📊 实时进度跟踪]
        E --> E3[⚡ 负载均衡]
    end
    
    subgraph "🗜️ 压缩与输出"
        C --> F[📦 ZIP_DEFLATED/STORED]
        F --> F1[🐘 Zip64大文件支持]
        F --> F2[🔒 SHA256校验生成]
        F --> F3[📋 元数据JSON生成]
    end
    
    subgraph "🧠 AI训练集成"
        C --> G[🤖 ZipImageDataset]
        G --> G1[🖼️ 懒加载]
        G --> G2[⚡ 缓存机制]
        G --> G3[🔄 变换管道]
    end
    
    classDef arch fill:#e3f2fd,stroke:#1565c0
    classDef pre fill:#f3e5f5,stroke:#7b1fa2
    classDef comp fill:#e8f5e8,stroke:#2e7d32
    classDef out fill:#fff3e0,stroke:#ef6c00
    classDef train fill:#fce4ec,stroke:#c2185b
    class A,B,C arch
    class D,D1,D2,D3,D4 pre
    class E,E1,E2,E3 comp
    class F,F1,F2,F3 out
    class G,G1,G2,G3 train
"""
