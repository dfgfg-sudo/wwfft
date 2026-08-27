retry_policy:
  max_attempts: 3
  backoff: exponential
  initial_interval: 1000
  backoff_factor: 2
fallback:
  - condition: timeout
    action: use_cache
  - condition: service_unavailable
    action: skip_and_log
  - condition: url_invalid
    action: return_friendly_message