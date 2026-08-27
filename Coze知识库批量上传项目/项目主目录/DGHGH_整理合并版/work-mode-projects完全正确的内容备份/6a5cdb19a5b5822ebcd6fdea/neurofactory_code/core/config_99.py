节点名称: 大模型_1
类型: llm
配置:
  model: deepseek-reasoner
  system_prompt: |
    # Coze企业级超级调度器 - 核心系统提示词
    {{复制上面的完整提示词}}
  user_prompt: "{{input}}"
  temperature: 0.1
  max_tokens: 2000
  output_format: text
  output_variable: output
  output_type: String