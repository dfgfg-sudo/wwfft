deployment:
  strategy: canary
  steps:
    - percentage: 10
      duration: 1h
    - percentage: 50
      duration: 2h
    - percentage: 100