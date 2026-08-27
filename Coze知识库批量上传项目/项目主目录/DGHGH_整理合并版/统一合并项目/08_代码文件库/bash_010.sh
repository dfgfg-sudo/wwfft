#!/bin/bash
# build.sh - 自动化构建脚本

# 1. 环境检查
check_environment() {
    echo "检查系统环境..."
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker未安装"
        exit 1
    fi
    
    # 检查磁盘空间
    local free_space=$(df -h / | awk 'NR==2 {print $4}')
    echo "可用磁盘空间: $free_space"
}

# 2. 清理旧构建
clean_previous_build() {
    echo "清理旧构建..."
    docker system prune -f --filter "until=24h"
    rm -rf dist/ node_modules/ .next/
}

# 3. 依赖安装
install_dependencies() {
    echo "安装依赖..."
    
    # 前端项目
    if [ -f "package.json" ]; then
        npm ci --prefer-offline --no-audit
    fi
    
    # Java项目
    if [ -f "pom.xml" ]; then
        mvn dependency:go-offline
    fi
    
    # Python项目
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --cache-dir .pip-cache
    fi
}

# 4. 运行测试
run_tests() {
    echo "运行测试..."
    
    # 单元测试
    npm test -- --coverage --passWithNoTests
    
    # 集成测试
    if [ -d "tests/integration" ]; then
        npm run test:integration
    fi
    
    # 生成测试报告
    if [ -f "coverage/lcov.info" ]; then
        bash <(curl -s https://codecov.io/bash)
    fi
}

# 5. 构建应用
build_application() {
    echo "构建应用..."
    
    # 前端构建
    npm run build
    
    # Docker构建
    docker build \
        --build-arg NODE_ENV=production \
        --label "version=${VERSION}" \
        --label "build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        -t ${IMAGE_NAME}:${VERSION} .
    
    # 多平台构建（如需）
    if command -v docker buildx &> /dev/null; then
        docker buildx create --use
        docker buildx build \
            --platform linux/amd64,linux/arm64 \
            -t ${IMAGE_NAME}:${VERSION} \
            --push .
    fi
}

# 主函数
main() {
    check_environment
    clean_previous_build
    install_dependencies
    run_tests
    build_application
}

# 执行
main "$@"