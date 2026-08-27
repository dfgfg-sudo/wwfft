flowchart LR
    A[开始节点] --> B[并行分支1<br/>链接读取A]
    A --> C[并行分支2<br/>链接读取B]
    A --> D[并行分支3<br/>用户输入]
    B --> E[变量聚合节点<br/>first_non_empty]
    C --> E
    D --> E
    E --> F[大模型处理]
    F --> G[结束节点]