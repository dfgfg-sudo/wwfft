"""
workflow:
  name: 多源链接智能处理系统
  version: 3.0
  trigger:
    type: webhook
    path: /api/process-urls
  nodes:
    - id: url_input
      type: start
      config:
        parameters:
          - name: urls
            type: array
            description: "待处理的URL列表"
          - name: text_input
            type: string
            description: "用户直接输入的文本"
          - name: target_platforms
            type: array
            description: "目标分发平台 [dingtalk, feishu, wechat]"
    - id: parallel_url_processor
      type: parallel
      config:
        max_concurrency: 5
        timeout: 30000
      branches:
        - for_each: urls
          do:
            - id: link_reader
              type: LinkReaderPlugin
              input:
                url: {{item}}
            - id: content_extractor
              type: code
              code: |
                function extract(data) {
                  if (data.pdf_content) return {type: 'pdf', content: data.pdf_content};
                  if (data.data?.content) return {type: 'html', content: data.data.content};
                  return {type: 'unknown', content: ''};
                }
    - id: variable_aggregator
      type: variable_aggregate
      config:
        inputs:
          - source: parallel_url_processor.results
            priority: 1
          - source: text_input
            priority: 2
        rule: first_non_empty
    - id: intent_recognition
      type: llm
      config:
        model: deepseek-reasoner
        system_prompt: |
          依据以下意图列表仅返回数字序号：
          1: 信息查询
          2: 内容摘要
          3: 竞品分析
          4: 其他
        user_prompt: |
          输入内容：{{variable_aggregator.output}}
    - id: ai_analysis
      type: llm
      config:
        model: deepseek-reasoner
        system_prompt: |
          生成核心摘要（200字内）、关键要点（3-5个）、行动建议
        user_prompt: |
          内容：{{variable_aggregator.output}}
          意图：{{intent_recognition.output}}
        temperature: 0.3
    - id: knowledge_store
      type: knowledge_base
      config:
        action: insert
        content: {{ai_analysis.full_report}}
    - id: multi_platform_distribution
      type: parallel
      config:
        branches:
          - id: dingtalk_notify
            condition: {{'dingtalk' in target_platforms}}
            plugin: DingTalk
            action: send_message
    - id: end
      type: end
      output:
        status: success
        summary: {{ai_analysis.summary}}
        intent: {{intent_recognition.output}}
"""
