#!/bin/bash
# omnineuro_start.sh

echo "🚀 启动 OmniNeuro ASI 超融合智能系统 v5.0"

# 检查依赖
pip install -r requirements.txt 2>/dev/null || {
    echo "📦 安装依赖..."
    pip install pandas numpy watchdog pyyaml cryptography scikit-learn pdfminer.six
}

# 创建目录结构
mkdir -p data models logs

# 检查配置文件
if [ ! -f "asi_config.yaml" ]; then
    echo "📄 创建默认配置文件..."
    cat > asi_config.yaml << 'EOL'
monitor_dirs:
  - ./data
model_store: ./models
max_concurrent: 4
auto_update: true
EOL
fi

# 启动系统
echo "🌟 启动系统..."
python omnineuro_asi.py