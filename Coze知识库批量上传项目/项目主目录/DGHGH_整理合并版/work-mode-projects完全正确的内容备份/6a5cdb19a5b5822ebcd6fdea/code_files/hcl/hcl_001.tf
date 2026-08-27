# Terraform 配置示例
resource "aws_ecs_cluster" "main" {
  name = "production-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family = "myapp"
  container_definitions = jsonencode([
    {
      name  = "myapp"
      image = "${var.docker_image}:${var.image_tag}"
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "main" {
  name            = "myapp-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 3
}