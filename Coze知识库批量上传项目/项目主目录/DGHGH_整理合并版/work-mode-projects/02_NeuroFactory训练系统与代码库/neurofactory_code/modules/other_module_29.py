"""
# 全自动处理（合并重复文件 + 内容对比 + 压缩）
python aidatasetpack.py -i /path/to/dataset -o dataset_v1.zip

# 禁用自动合并（保留所有文件，仅压缩）
python aidatasetpack.py -i ./data -o data.zip --no-merge

# 增加线程数以提升速度
python aidatasetpack.py -i ./bigdata -o big.zip -w 16
"""
