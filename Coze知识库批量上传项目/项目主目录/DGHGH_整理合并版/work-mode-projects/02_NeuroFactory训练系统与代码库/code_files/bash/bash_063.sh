curl -X POST "http://localhost:8000/predict" \\
  -H "Content-Type: application/json" \\
  -d '{"features": [0.1, 0.2, 0.3, ...]}'