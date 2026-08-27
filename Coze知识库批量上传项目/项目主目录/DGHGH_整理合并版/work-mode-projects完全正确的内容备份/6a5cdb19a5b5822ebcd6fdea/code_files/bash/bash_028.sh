# 示例CSV数据
echo "name,age,score\nAlice,25,89\nBob,30,92" > data_input/sample.csv

# 示例JSON数据
echo '{"task": "training", "params": {"lr": 0.01}}' > data_input/config.json

# 示例文本数据
echo "OmniNeuro ASI 是超融合智能系统" > data_input/note.txt

# 验证方法：将测试文件放入 data_input 目录
echo "name,age\nAlice,25\nBob,30" > data_input/test.csv
echo '{"key":"value"}' > data_input/test.json