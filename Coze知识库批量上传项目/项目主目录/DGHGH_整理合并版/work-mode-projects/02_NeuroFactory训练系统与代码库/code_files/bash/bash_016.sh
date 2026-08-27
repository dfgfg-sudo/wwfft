#!/bin/bash
# security-scan.sh

# 1. 依赖安全扫描
echo "扫描依赖漏洞..."
npm audit --audit-level=high

# 2. 容器镜像扫描
if [ -f "Dockerfile" ]; then
    echo "扫描Docker镜像..."
    
    # 使用Trivy
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v $PWD:/tmp \
        aquasec/trivy image \
        --severity HIGH,CRITICAL \
        --exit-code 1 \
        ${IMAGE_NAME}:${VERSION}
    
    # 使用Snyk
    if command -v snyk &> /dev/null; then
        snyk container test ${IMAGE_NAME}:${VERSION} \
            --severity-threshold=🔄 CI/CD自动化操作详解

一、CI/CD核心概念

1. 什么是CI/CD？