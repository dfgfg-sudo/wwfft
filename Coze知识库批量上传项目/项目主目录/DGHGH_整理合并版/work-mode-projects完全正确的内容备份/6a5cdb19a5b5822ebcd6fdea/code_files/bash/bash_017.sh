#!/bin/bash

# Neuro Factory Pro 启动脚本

set -e

echo "🌌 启动 Neuro Factory Pro..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./deploy.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
python -c "import torch, transformers, gradio" || {
    echo "❌ 依赖检查失败"
    exit 1
}

# 启动系统
echo "🚀 启动系统..."
python main.py "$@"

# 如果启动失败
if [ $? -ne 0 ]; then
    echo "❌ 启动失败"
    echo "📋 调试建议:"
    echo "  1. 检查端口 7860 是否被占用"
    echo "  2. 查看日志文件: neuro_factory.log"
    echo "  3. 重新安装依赖: pip install -r requirements.txt"
    exit 1
fi