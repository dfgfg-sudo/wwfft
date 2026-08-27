# 1. 安装依赖
pip install -r requirements.txt

# 2. 准备数据（将数据文件放入 data/ 目录）
# 3. 训练
python main.py --mode train --config config.json

# 4. 评估最佳模型
python main.py --mode evaluate --checkpoint best_model.pth

# 5. 预测
python main.py --mode predict --checkpoint best_model.pth

# 6. 导出 ONNX
python main.py --mode export --format onnx --checkpoint best_model.pth

# 7. 运行演示（5个epoch）
python main.py --mode demo