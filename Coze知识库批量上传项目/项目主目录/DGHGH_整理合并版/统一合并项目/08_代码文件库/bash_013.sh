#!/bin/bash

# Neuro Factory Pro 部署脚本
# 版本: v3.14

set -e

echo "🚀 开始部署 Neuro Factory Pro..."

# 检查Python版本
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python 版本: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "❌ 需要 Python 3.8 或更高版本"
    exit 1
fi

# 创建虚拟环境
echo "📦 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 创建必要目录
echo "📁 创建目录结构..."
mkdir -p data
mkdir -p models
mkdir -p logs
mkdir -p configs
mkdir -p tests

# 复制配置文件
echo "⚙️  复制配置文件..."
if [ ! -f "configs/default.yaml" ]; then
    cp configs/default.yaml.example configs/default.yaml
fi

# 设置权限
echo "🔐 设置权限..."
chmod +x main.py
chmod +x deploy.sh
chmod +x run.sh

# 运行测试
echo "🧪 运行测试..."
if [ -f "test_integration.py" ]; then
    python test_integration.py
    if [ $? -ne 0 ]; then
        echo "❌ 测试失败，请检查"
        exit 1
    fi
fi

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 使用说明:"
echo "  1. 启动系统: ./run.sh"
echo "  2. 访问界面: http://localhost:7860"
echo "  3. 查看日志: tail -f neuro_factory.log"
echo ""
echo "🌌 Neuro Factory Pro 已就绪！"