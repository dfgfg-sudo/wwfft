"""
workflow:
  name: 多源链接智能处理系统
  version: 2.0
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
          你是一位杰出的意图识别专家。
          依据以下意图列表仅返回与之对应的数字序号：
          1: 信息查询
          2: 内容摘要
          3: 竞品分析
          4: 其他
        user_prompt: |
          输入内容：{{variable_aggregator.output}}
          请分析用户意图仅返回数字序号
    - id: ai_analysis
      type: llm
      config:
        model: deepseek-reasoner
        system_prompt: |
          你是一个内容分析师。请基于以下内容生成：
          1. 核心摘要（200字以内）
          2. 关键要点（3-5个）
          3. 行动建议
        user_prompt: |
          内容：{{variable_aggregator.output}}
          意图类型：{{intent_recognition.output}}
        temperature: 0.3
    - id: knowledge_store
      type: knowledge_base
      config:
        action: insert
        content: {{ai_analysis.full_report}}
        metadata:
          source_urls: {{urls}}
          intent: {{intent_recognition.output}}
          timestamp: {{current_time}}
    - id: multi_platform_distribution
      type: parallel
      config:
        branches:
          - id: dingtalk_notify
            condition: {{'dingtalk' in target_platforms}}
            plugin: DingTalk
            action: send_message
            config:
              webhook: {{dingtalk_webhook}}
              content: |
                ## 智能处理报告
                摘要：{{ai_analysis.summary}}
                要点：{{ai_analysis.key_points}}
          - id: feishu_sheet
            condition: {{'feishu' in target_platforms}}
            plugin: Feishu
            action: append_to_sheet
            config:
              sheet_id: {{sheet_id}}
              data:
                - {{current_time}}
                - {{urls|join(', ')}}
                - {{ai_analysis.summary}}
    - id: end
      type: end
      output:
        status: success
        processed_urls: {{urls}}
        summary: {{ai_analysis.summary}}
        intent: {{intent_recognition.output}}
        knowledge_id: {{knowledge_store.id}}
        distributions: {{multi_platform_distribution.results}}
"""
