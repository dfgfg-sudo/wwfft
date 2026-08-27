groups:
- name: coze_workflows
  rules:
  - alert: HighFailureRate
    expr: rate(coze_workflow_failures{workflow="order_processing"}[5m]) > 0.05
    for: 10m
    annotations:
      summary: "工作流 {{ $labels.workflow }} 失败率过高"