// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        PROJECT_NAME = 'my-app'
        KUBE_NAMESPACE = 'production'
    }
    
    stages {
        stage('代码检出') {
            steps {
                git branch: 'main', 
                    url: 'git@github.com:user/repo.git',
                    credentialsId: 'github-ssh-key'
            }
        }
        
        stage('代码质量') {
            parallel {
                stage('静态分析') {
                    steps {
                        sh 'npm run lint'
                        sh 'sonar-scanner'
                    }
                }
                stage('单元测试') {
                    steps {
                        sh 'npm test'
                        junit 'reports/**/*.xml'
                    }
                }
            }
        }
        
        stage('构建镜像') {
            steps {
                script {
                    docker.build("${DOCKER_REGISTRY}/${PROJECT_NAME}:${env.BUILD_ID}")
                }
            }
        }
        
        stage('安全扫描') {
            steps {
                sh '''
                    docker scan --file Dockerfile \
                    ${DOCKER_REGISTRY}/${PROJECT_NAME}:${env.BUILD_ID}
                '''
            }
        }
        
        stage('推送镜像') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-credentials') {
                        docker.image("${DOCKER_REGISTRY}/${PROJECT_NAME}:${env.BUILD_ID}").push()
                        docker.image("${DOCKER_REGISTRY}/${PROJECT_NAME}:latest").push()
                    }
                }
            }
        }
        
        stage('部署到测试环境') {
            steps {
                sh """
                    kubectl set image deployment/myapp \
                    app=${DOCKER_REGISTRY}/${PROJECT_NAME}:${env.BUILD_ID} \
                    -n staging
                    
                    kubectl rollout status deployment/myapp -n staging
                """
            }
        }
        
        stage('集成测试') {
            steps {
                sh 'npm run test:e2e'
            }
        }
        
        stage('部署到生产环境') {
            input {
                message "是否部署到生产环境?"
                ok "确认部署"
                parameters {
                    string(name: 'VERSION', defaultValue: "${env.BUILD_ID}", 
                           description: '要部署的版本号')
                }
            }
            steps {
                sh """
                    kubectl set image deployment/myapp \
                    app=${DOCKER_REGISTRY}/${PROJECT_NAME}:${VERSION} \
                    -n ${KUBE_NAMESPACE}
                    
                    kubectl rollout status deployment/myapp -n ${KUBE_NAMESPACE}
                """
            }
        }
        
        stage('监控与验证') {
            steps {
                sh '''
                    sleep 30
                    # 检查应用健康状态
                    curl -f http://production-app/health
                    
                    # 检查日志
                    kubectl logs deployment/myapp --tail=50 -n production
                '''
            }
        }
    }
    
    post {
        success {
            slackSend(color: 'good', message: "构建 ${env.JOB_NAME} #${env.BUILD_NUMBER} 成功")
        }
        failure {
            slackSend(color: 'danger', message: "构建 ${env.JOB_NAME} #${env.BUILD_NUMBER} 失败")
        }
    }
}