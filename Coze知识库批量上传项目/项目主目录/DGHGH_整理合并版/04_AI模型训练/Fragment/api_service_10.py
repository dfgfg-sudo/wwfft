"""
graph TD
    subgraph 前端
        A[React 18 + TypeScript] --> B[Ant Design 5.x]
        A --> C[ECharts 5.x]
        A --> D[Redux Toolkit]
        D --> E[Vite 4.x]
    end
    
    subgraph 后端
        F[Spring Boot 3.x] --> G[Spring Cloud]
        F --> H[OpenAPI 3.0]
        F --> I[JWT + OAuth2.0]
        J[Camunda 7.x] --> F
    end
    
    subgraph AI
        K[TensorFlow Serving] --> L[PyTorch]
        K --> M[Coze官方模型]
    end
    
    subgraph 数据
        N[PostgreSQL 14+] --> O[Redis 7.x]
        N --> P[MongoDB 6.x]
        Q[Apache Kafka 3.x] --> N
    end
    
    subgraph 基础设施
        R[Docker] --> S[Kubernetes]
        S --> T[Istio 1.18+]
        U[Prometheus + Grafana] --> V[ELK Stack]
    end
"""
