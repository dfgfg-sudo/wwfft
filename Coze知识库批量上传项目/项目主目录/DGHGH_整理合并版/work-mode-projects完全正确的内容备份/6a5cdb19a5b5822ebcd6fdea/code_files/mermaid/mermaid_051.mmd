sequenceDiagram
    participant U as 用户
    participant S as 智能体
    participant B as 银行API
    participant Q as 券商API
    participant P as 返利平台
    
    Note over S: 00:00 唤醒
    S->>B: 查询所有账户余额
    B-->>S: 返回余额
    S->>S: 计算今日可投资金
    
    Note over S: 09:15 开盘前
    S->>Q: 自动申购可转债（风控校验通过）
    Q-->>S: 申购成功
    
    Note over S: 13:00 国债逆回购
    S->>Q: 借出1天期逆回购
    Q-->>S: 成交
    
    Note over S: 14:50 基金定投（可选，用户已关闭）
    S->>S: 跳过（零亏损模式）
    
    Note over S: 15:30 银行理财调仓
    S->>B: 将多余资金转入T+0理财
    
    Note over S: 20:00 返利/问卷任务
    S->>P: 自动完成合规问卷
    P-->>S: 返利到账
    
    Note over S: 23:50 日终清算
    S->>S: 计算今日总收益
    S->>S: 划转10%到准备金池
    S->>U: 发送日报告（收益、操作、准备金余额）