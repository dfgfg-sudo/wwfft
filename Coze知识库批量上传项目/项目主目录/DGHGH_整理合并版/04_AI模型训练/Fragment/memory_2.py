"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-automation
  namespace: coze
  labels:
    app: unified-automation
    version: v15
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unified-automation
  template:
    metadata:
      labels:
        app: unified-automation
        version: v15
    spec:
      containers:
      - name: api
        image: unified-automation/center:15.0.0
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        - name: DB_URL
          value: "jdbc:postgresql://postgres-svc:5432/ewio_db"
        - name: REDIS_HOST
          value: "redis-svc"
        - name: MONGO_URI
          value: "mongodb://mongodb-svc:27017/ewio_ai_db"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: unified-automation-svc
  namespace: coze
spec:
  selector:
    app: unified-automation
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: unified-automation-hpa
  namespace: coze
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: unified-automation
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""
