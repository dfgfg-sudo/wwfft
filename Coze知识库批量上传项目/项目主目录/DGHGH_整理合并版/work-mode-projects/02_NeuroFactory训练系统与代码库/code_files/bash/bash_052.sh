# 创建测试文件
echo "这是测试文档" > data/doc1.txt
echo '{"key": "value"}' > data/data1.json

# 运行单次处理
python omnineuro_asi.py --data-dir data

# 查看模型输出
ls models/
# 输出示例：singularity_v2.enc

# 查看日志
cat omnineuro.log