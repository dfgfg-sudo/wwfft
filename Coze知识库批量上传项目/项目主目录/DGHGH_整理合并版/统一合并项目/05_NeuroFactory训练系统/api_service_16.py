"""
graph TB
    subgraph 决策层
        A[确定性策略引擎] --> B[零亏损策略池]
        C[收益增强模块] --> D[返利/奖励自动化]
    end
    subgraph 风控层
        E[三源数据校验] 
        F[沙箱预执行]
        G[熔断与回滚]
    end
    subgraph 执行层
        H[券商API集群]
        I[银行API集群]
        J[返利平台自动化]
    end
    subgraph 责任转移层
        K[风险准备金池]
        L[操作确认系统]
        M[多账户分散]
    end
    B --> H & I
    D --> J
    E & F & G --> H & I & J
    K & L & M -.-> 用户
"""
