# AWS ECS
aws ecs create-cluster --cluster-name autocodepro
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs create-service --cluster autocodepro --service-name api --task-definition autocodepro-api

# Azure Web Apps
az webapp up --name autocodepro-api --resource-group autocodepro-rg --runtime "NODE|18-lts"

# Google Cloud Run
gcloud run deploy autocodepro-api --image gcr.io/project-id/autocodepro-api --platform managed