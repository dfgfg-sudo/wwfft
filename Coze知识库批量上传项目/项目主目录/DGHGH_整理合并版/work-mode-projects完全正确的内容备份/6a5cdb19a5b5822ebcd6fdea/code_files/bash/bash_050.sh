# 使用Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 使用Docker Swarm
docker stack deploy -c docker-compose.yml autocodepro

# 使用Kubernetes
kubectl apply -f kubernetes/