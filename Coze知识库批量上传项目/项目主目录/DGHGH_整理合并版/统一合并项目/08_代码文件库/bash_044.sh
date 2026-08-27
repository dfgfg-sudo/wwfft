# 启动Web界面
python main.py --mode web --port 7860

# 启动训练流水线
python main.py --mode train --data ./data/input

# 启动推理服务
python main.py --mode infer --input "你的问题"

# 启动API服务器
python main.py --mode api --port 8000

# 使用CLI模式
python main.py --mode cli