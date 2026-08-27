# 安装依赖
pip install pandas numpy watchdog pyyaml scikit-learn pdfminer.six

# 创建配置文件
cat > asi_config.yaml <<EOL
monitor_dirs:
  - ./data_input
  - ./knowledge
  - ./archive
model_store: ./models
max_concurrent: 4
auto_update: true
max_file_size: 104857600
EOL

# 创建数据目录
mkdir -p data_input models