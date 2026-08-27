"""
retry_policy:
  max_attempts: 3
  backoff: exponential
fallback:
  - condition: timeout
    action: use_cache
  - condition: service_unavailable
    action: skip_and_log
"""
