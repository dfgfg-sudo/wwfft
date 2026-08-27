flowchart TD
    A[用户输入多个URL+文本] --> B[并行处理URL列表]
    B --> C[LinkReaderPlugin<br/>读取网页/PDF/图片]
    C --> D[变量聚合<br/>合并所有内容]
    D --> E[意图识别<br/>大模型节点]
    E --> F[AI分析<br/>摘要/要点/建议]
    F --> G[存入知识库]
    F --> H[多平台分发]
    H --> I[钉钉推送]
    H --> J[飞书表格]
    G --> K[结束节点返回结果]
    I --> K
    J --> K