# 使用 HashiCorp Vault 或 Kubernetes Secrets
# secrets.yaml (加密存储)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: <base64-encoded>
  api-key: <base64-encoded>
  jwt-secret: <base64-encoded>