节点名称: 总结大模型
模型: deepseek-reasoner
系统提示词: |
  你是一个内容分析师。请基于以下内容生成：
  1. 核心摘要（200字以内）
  2. 关键要点（3-5个）
  3. 行动建议
输入:
  - content: {{variable_aggregator.output}}
  - intent: {{intent_recognition.output}}
temperature: 0.3