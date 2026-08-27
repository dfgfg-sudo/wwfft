"""
groups:
- name: unified-automation
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "错误率超过5%"
  - alert: SlowResponse
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 3
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "响应时间超过3秒"
"""
